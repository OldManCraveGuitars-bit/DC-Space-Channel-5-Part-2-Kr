using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Drawing;
using System.IO;
using System.IO.Compression;
using System.Security.Cryptography;
using System.Text;
using System.Web.Script.Serialization;
using System.Windows.Forms;

// The builder pins the entire patch, including original/result file hashes.
// Original files are opened for reading only. A new folder is published only
// after every result hash matches; existing output folders are never replaced.
internal static class PatchApplier {
    const string PatchHash = "f620dc48e48697d37c676e6307175534b477b642efcdc84ba34a8aad8c37fff9";
    const string BuildLabel = "비공식 한글판 정식 버전 V1.104";
    const long PatchBytes = 30299911L;
    sealed class Range { public long Offset, SourceOffset = -1; public int Length; public byte[] Bytes; }
    sealed class FilePatch {
        public string Name, SourceHash, ResultHash;
        public long Size;
        public List<Range> Ranges = new List<Range>();
    }
    static string Hex(byte[] raw) { return BitConverter.ToString(raw).Replace("-", "").ToLowerInvariant(); }
    static string Hash(string path, Action<string> progress) {
        using (var file = new FileStream(path, FileMode.Open, FileAccess.Read, FileShare.Read))
        using (var sha = SHA256.Create()) {
            byte[] buffer = new byte[1024 * 1024]; int n; long done = 0, last = -1;
            while ((n = file.Read(buffer, 0, buffer.Length)) > 0) {
                sha.TransformBlock(buffer, 0, n, buffer, 0); done += n;
                long percent = file.Length == 0 ? 100 : done * 100 / file.Length;
                if (percent / 10 != last) { last = percent / 10; progress(Path.GetFileName(path) + " " + percent + "%"); }
            }
            sha.TransformFinalBlock(new byte[0], 0, 0); return Hex(sha.Hash);
        }
    }
    static byte[] Exact(BinaryReader reader, int size) {
        byte[] raw = reader.ReadBytes(size);
        if (raw.Length != size) throw new InvalidDataException("패치 파일이 잘렸습니다.");
        return raw;
    }
    static List<FilePatch> ReadPatch(string path) {
        if (Hash(path, delegate(string s) {}) != PatchHash) throw new InvalidDataException("패치 파일 검사가 실패했습니다.");
        using (var compressed = File.OpenRead(path))
        using (var gzip = new GZipStream(compressed, CompressionMode.Decompress))
        using (var memory = new MemoryStream()) {
            byte[] buffer = new byte[65536]; int n;
            while ((n = gzip.Read(buffer, 0, buffer.Length)) > 0) {
                if (memory.Length + n > PatchBytes) throw new InvalidDataException("패치 크기 제한을 넘었습니다.");
                memory.Write(buffer, 0, n);
            }
            memory.Position = 0;
            using (var reader = new BinaryReader(memory, Encoding.UTF8)) {
                string magic = Encoding.ASCII.GetString(Exact(reader, 8)); uint version = reader.ReadUInt32();
                if ((version != 1 && version != 2) || magic != "SC5P2KR" + version || reader.ReadUInt32() != 4)
                    throw new InvalidDataException("지원하지 않는 패치 형식입니다.");
                var result = new List<FilePatch>(); var names = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
                for (int i = 0; i < 4; ++i) {
                    uint nameSize = reader.ReadUInt32();
                    if (nameSize == 0 || nameSize > 512) throw new InvalidDataException("잘못된 파일 이름입니다.");
                    string name = new UTF8Encoding(false, true).GetString(Exact(reader, (int)nameSize));
                    if (Path.GetFileName(name) != name || name == "." || name == ".." || Path.IsPathRooted(name)
                        || name.IndexOfAny(Path.GetInvalidFileNameChars()) >= 0 || !names.Add(name))
                        throw new InvalidDataException("잘못된 파일 경로입니다.");
                    var f = new FilePatch { Name = name, Size = reader.ReadInt64(),
                        SourceHash = Hex(Exact(reader, 32)), ResultHash = Hex(Exact(reader, 32)) };
                    uint count = reader.ReadUInt32(); long priorEnd = 0;
                    if (f.Size < 0 || count > 1000000) throw new InvalidDataException("잘못된 패치 범위입니다.");
                    for (uint j = 0; j < count; ++j) {
                        byte kind = version == 2 ? reader.ReadByte() : (byte)0;
                        long offset = reader.ReadInt64(); uint length = reader.ReadUInt32();
                        if (kind > 1 || length == 0 || length > 1024 * 1024 || offset < priorEnd || offset > f.Size - length)
                            throw new InvalidDataException("겹치거나 벗어난 패치 범위입니다.");
                        var range = new Range { Offset = offset, Length = (int)length };
                        if (kind == 0) range.Bytes = Exact(reader, (int)length);
                        else {
                            range.SourceOffset = reader.ReadInt64();
                            if (range.SourceOffset < 0 || range.SourceOffset > f.Size - length)
                                throw new InvalidDataException("원본 복사 범위가 벗어났습니다.");
                        }
                        f.Ranges.Add(range);
                        priorEnd = offset + length;
                    }
                    result.Add(f);
                }
                if (memory.Length != PatchBytes || memory.Position != memory.Length) throw new InvalidDataException("패치 크기 또는 끝 검사가 실패했습니다.");
                return result;
            }
        }
    }
    // This layout is specific to the hash-pinned three-track Japanese dump.
    // INDEX 01 of track 2 follows its 150-sector pregap. Keep audio bytes in
    // their original order and preserve the high-density start at LBA 45000.
    static List<object> ConvertToGdi(string folder, List<FilePatch> files, Action<string> progress) {
        const string prefix = "Space Channel 5 Part 2 (Japan)";
        const string gdi = "3\n1 0 4 2352 track01.bin 0\n2 992 0 2352 track02.raw 0\n3 45000 4 2352 track03.bin 0\n";
        const string audioHash = "ced05b98c256a32b3d0f1c565834726c378d059245496051f4896af82dbd5a97";
        const string gdiHash = "abb78c115a0179dfc2af5271817eb97e18baa2704253bac821bb44d8def5d5f7";
        string audioSource = Path.Combine(folder, prefix + " (Track 2).bin");
        string audioResult = Path.Combine(folder, "track02.raw");
        progress("ODE용 GDI 구성: 트랙과 프리갭 정리");
        using (var source = File.OpenRead(audioSource))
        using (var target = new FileStream(audioResult, FileMode.CreateNew, FileAccess.Write, FileShare.None)) {
            if (source.Length != 2076816) throw new InvalidDataException("Track 2 크기가 다릅니다.");
            source.Position = 150L * 2352;
            source.CopyTo(target); target.Flush(true);
        }
        if (new FileInfo(audioResult).Length != 1724016 || Hash(audioResult, progress) != audioHash)
            throw new InvalidDataException("GDI 오디오 트랙 검사 실패");
        string descriptor = Path.Combine(folder, "disc.gdi");
        File.WriteAllText(descriptor, gdi, new UTF8Encoding(false));
        if (Hash(descriptor, progress) != gdiHash) throw new InvalidDataException("GDI 설명 파일 검사 실패");
        var result = new List<object>();
        foreach (var f in files) {
            string name = f.Name == prefix + " (Track 1).bin" ? "track01.bin" : f.Name == prefix + " (Track 3).bin" ? "track03.bin" : null;
            if (name == null) continue;
            File.Move(Path.Combine(folder, f.Name), Path.Combine(folder, name));
            result.Add(new { name = name, size = f.Size, sha256 = f.ResultHash });
        }
        if (result.Count != 2) throw new InvalidDataException("GDI 데이터 트랙 구성 실패");
        // Remove only redundant files created by this invocation in its new
        // temporary directory. The original source folder is never mutated.
        File.Delete(audioSource);
        File.Delete(Path.Combine(folder, prefix + ".cue"));
        result.Add(new { name = "track02.raw", size = 1724016, sha256 = audioHash });
        result.Add(new { name = "disc.gdi", size = 83, sha256 = gdiHash });
        return result;
    }
    static object Apply(string patch, string source, string output, string format, Action<string> progress) {
        if (format != "cue" && format != "gdi") throw new ArgumentException("출력 형식은 cue 또는 gdi입니다.");
        source = Path.GetFullPath(File.Exists(source) ? Path.GetDirectoryName(source) : source).TrimEnd(Path.DirectorySeparatorChar);
        output = Path.GetFullPath(output).TrimEnd(Path.DirectorySeparatorChar);
        if (!Directory.Exists(source)) throw new DirectoryNotFoundException("원본 폴더를 찾을 수 없습니다.");
        if (output.Equals(source, StringComparison.OrdinalIgnoreCase) || output.StartsWith(source + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase))
            throw new IOException("원본 폴더 밖의 새 폴더를 선택하세요.");
        if (Directory.Exists(output) || File.Exists(output)) throw new IOException("결과 폴더가 이미 있습니다. 새 폴더를 선택하세요.");
        var files = ReadPatch(patch);
        foreach (var f in files) {
            string path = Path.Combine(source, f.Name);
            if (!File.Exists(path) || new FileInfo(path).Length != f.Size) throw new InvalidDataException("일본판 원본 파일이 필요합니다: " + f.Name);
            progress("원본 검사: " + f.Name);
            if (Hash(path, progress) != f.SourceHash) throw new InvalidDataException("원본 해시가 다릅니다: " + f.Name);
        }
        string parent = Path.GetDirectoryName(output); Directory.CreateDirectory(parent);
        string temporary = output + ".building-" + Guid.NewGuid().ToString("N");
        if (Directory.Exists(temporary) || File.Exists(temporary)) throw new IOException("작업 폴더를 만들 수 없습니다.");
        Directory.CreateDirectory(temporary);
        var results = new List<object>();
        foreach (var f in files) {
            string src = Path.Combine(source, f.Name), dst = Path.Combine(temporary, f.Name);
            progress("복사 및 적용: " + f.Name);
            using (var original = new FileStream(src, FileMode.Open, FileAccess.Read, FileShare.Read))
            using (var target = new FileStream(dst, FileMode.CreateNew, FileAccess.ReadWrite, FileShare.None)) {
                original.CopyTo(target, 1024 * 1024);
                byte[] copyBuffer = new byte[65536];
                foreach (var range in f.Ranges) {
                    target.Position = range.Offset;
                    if (range.SourceOffset < 0) target.Write(range.Bytes, 0, range.Bytes.Length);
                    else {
                        original.Position = range.SourceOffset; int remaining = range.Length;
                        while (remaining > 0) {
                            int n = original.Read(copyBuffer, 0, Math.Min(remaining, copyBuffer.Length));
                            if (n == 0) throw new InvalidDataException("원본 복사 범위가 잘렸습니다.");
                            target.Write(copyBuffer, 0, n); remaining -= n;
                        }
                    }
                }
                target.Flush(true);
            }
            progress("결과 검사: " + f.Name);
            if (new FileInfo(dst).Length != f.Size || Hash(dst, progress) != f.ResultHash)
                throw new InvalidDataException("결과 검사가 실패했습니다. 작업 폴더: " + temporary);
            results.Add(new { name = f.Name, size = f.Size, sha256 = f.ResultHash, changed_ranges = f.Ranges.Count });
        }
        if (format == "gdi") results = ConvertToGdi(temporary, files, progress);
        Directory.Move(temporary, output);
        progress("완료: " + output);
        return new { status = "passed", build = BuildLabel, source = source, output = output,
            format = format, patch_sha256 = PatchHash, originals_opened_read_only = true, all_result_hashes_verified = true, files = results };
    }
    static Form Window() {
        var form = new Form { Text = "스페이스 채널 5 파트 2 한국어 패치", ClientSize = new Size(610, 405),
            Font = new Font("맑은 고딕", 10), FormBorderStyle = FormBorderStyle.FixedDialog, MaximizeBox = false,
            StartPosition = FormStartPosition.CenterScreen };
        var header = new Label { Text = "한국어 패치 · " + BuildLabel, Location = new Point(20, 15), AutoSize = true };
        var note = new Label { Text = "일본판 원본 CUE와 트랙 파일 3개가 필요합니다.\n원본을 검사한 뒤 새 폴더에 결과를 만듭니다.", Location = new Point(20, 45), Size = new Size(570, 45) };
        var sourceLabel = new Label { Text = "원본 CUE / 폴더", Location = new Point(20, 100), AutoSize = true };
        var source = new TextBox { Location = new Point(20, 125), Size = new Size(470, 27) };
        var browse = new Button { Text = "찾아보기", Location = new Point(500, 122), Size = new Size(90, 32) };
        var outLabel = new Label { Text = "새 결과 폴더", Location = new Point(20, 165), AutoSize = true };
        var output = new TextBox { Location = new Point(20, 190), Size = new Size(470, 27) };
        var outBrowse = new Button { Text = "위치 선택", Location = new Point(500, 187), Size = new Size(90, 32) };
        var formatLabel = new Label { Text = "출력 형식", Location = new Point(20, 238), AutoSize = true };
        var format = new ComboBox { Location = new Point(105, 234), Size = new Size(485, 28), DropDownStyle = ComboBoxStyle.DropDownList };
        format.Items.AddRange(new object[] { "GDI · GDEMU / MODE 등 ODE용", "CUE + BIN · 기존 형식" });
        format.SelectedIndex = 0;
        var status = new Label { Text = "원본과 결과 위치를 선택하세요.", Location = new Point(20, 280), Size = new Size(570, 55) };
        var apply = new Button { Text = "패치 적용", Location = new Point(450, 348), Size = new Size(140, 37) };
        form.Controls.AddRange(new Control[] { header, note, sourceLabel, source, browse, outLabel, output, outBrowse, formatLabel, format, status, apply });
        browse.Click += delegate { using (var dialog = new OpenFileDialog { Filter = "Dreamcast CUE (*.cue)|*.cue", CheckFileExists = true }) if (dialog.ShowDialog(form) == DialogResult.OK) source.Text = dialog.FileName; };
        outBrowse.Click += delegate { using (var dialog = new FolderBrowserDialog { Description = "결과 폴더를 만들 상위 위치를 선택하세요." }) if (dialog.ShowDialog(form) == DialogResult.OK) output.Text = Path.Combine(dialog.SelectedPath, "Space Channel 5 Part 2 - KR"); };
        apply.Click += delegate {
            if (String.IsNullOrWhiteSpace(source.Text) || String.IsNullOrWhiteSpace(output.Text)) { status.Text = "원본과 결과 위치를 입력하세요."; return; }
            string src = source.Text, dst = output.Text, selectedFormat = format.SelectedIndex == 0 ? "gdi" : "cue";
            var worker = new BackgroundWorker { WorkerReportsProgress = true };
            apply.Enabled = browse.Enabled = outBrowse.Enabled = source.Enabled = output.Enabled = format.Enabled = false;
            form.ControlBox = false;
            worker.DoWork += delegate(object sender, DoWorkEventArgs e) {
                e.Result = Apply(Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "SC5P2KR.patch.gz"), src, dst, selectedFormat, delegate(string s) { worker.ReportProgress(0, s); });
            };
            worker.ProgressChanged += delegate(object sender, ProgressChangedEventArgs e) { status.Text = (string)e.UserState; };
            worker.RunWorkerCompleted += delegate(object sender, RunWorkerCompletedEventArgs e) {
                apply.Enabled = browse.Enabled = outBrowse.Enabled = source.Enabled = output.Enabled = format.Enabled = true; form.ControlBox = true;
                status.Text = e.Error == null ? (selectedFormat == "gdi" ? "완료했습니다. 결과 폴더의 파일 4개를 ODE에 복사하세요.\n" : "완료했습니다. 결과 폴더의 CUE를 실행하세요.\n") + dst : e.Error.Message;
                worker.Dispose();
            };
            worker.RunWorkerAsync();
        };
        return form;
    }
    static int ApplyCli(string[] args) {
        string source = Path.GetFullPath(File.Exists(args[2]) ? Path.GetDirectoryName(args[2]) : args[2]).TrimEnd(Path.DirectorySeparatorChar);
        string output = Path.GetFullPath(args[3]).TrimEnd(Path.DirectorySeparatorChar);
        string report = Path.GetFullPath(args[4]);
        if (report.Equals(source, StringComparison.OrdinalIgnoreCase) || report.StartsWith(source + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase)
            || report.Equals(output, StringComparison.OrdinalIgnoreCase) || report.StartsWith(output + Path.DirectorySeparatorChar, StringComparison.OrdinalIgnoreCase))
            throw new IOException("검증 기록은 원본과 결과 폴더 밖에 저장하세요.");
        // CreateNew and the held exclusive handle prevent a CLI report from
        // overwriting an existing file, including an original ROM track.
        using (var file = new FileStream(report, FileMode.CreateNew, FileAccess.Write, FileShare.None)) {
            object result; int code;
            try { result = Apply(args[1], args[2], args[3], args.Length == 6 ? args[5].ToLowerInvariant() : "cue", delegate(string s) {}); code = 0; }
            catch (Exception e) { result = new { status = "rejected", error = e.Message }; code = 1; }
            byte[] raw = new UTF8Encoding(false).GetBytes(new JavaScriptSerializer().Serialize(result));
            file.Write(raw, 0, raw.Length); file.Flush(true); return code;
        }
    }
    [STAThread] static int Main(string[] args) {
        try {
            if ((args.Length == 5 || args.Length == 6) && args[0] == "--apply") {
                return ApplyCli(args);
            }
            if (args.Length == 2 && args[0] == "--render-ui") {
                Application.EnableVisualStyles();
                using (var form = Window()) {
                    form.ShowInTaskbar = false; form.StartPosition = FormStartPosition.Manual;
                    form.Location = new Point(-20000, -20000); form.Opacity = 0;
                    form.Show(); Application.DoEvents();
                    using (var bitmap = new Bitmap(form.Width, form.Height)) { form.DrawToBitmap(bitmap, new Rectangle(0, 0, form.Width, form.Height)); bitmap.Save(args[1]); }
                    form.Close();
                }
                return 0;
            }
            if (args.Length != 0) throw new ArgumentException("지원하지 않는 실행 옵션입니다.");
            Application.EnableVisualStyles(); Application.SetCompatibleTextRenderingDefault(false); Application.Run(Window()); return 0;
        } catch (Exception e) {
            if (!((args.Length == 5 || args.Length == 6) && args[0] == "--apply")) MessageBox.Show(e.Message, "패치 적용 실패", MessageBoxButtons.OK, MessageBoxIcon.Error);
            return 1;
        }
    }
}
