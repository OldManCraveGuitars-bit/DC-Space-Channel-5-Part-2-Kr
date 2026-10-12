/* Part 2 buffered-list subtitles and source playback observer.
 * Diagnostic drawing is an explicit trial-build option, never a translation.
 */
typedef unsigned int u32;
typedef unsigned short u16;
typedef unsigned char u8;
typedef struct { u32 bank,member,start_ms,end_ms; const u16 *text; u32 box_bottom; } Subtitle;
typedef struct { u32 fingerprint_a,fingerprint_b,bank,member,frequency,samples; } SourceIdentity;
#include "voice_subtitle_data.h"
#include "voice_subtitle_alias_data09.h"
extern void original_subtitle_frame_end(void);
extern void original_subtitle_stream_open(void *,u32,u32);
extern void original_subtitle_afs_start(void *,u32,u32);
extern void original_subtitle_fname_start(void *,const char *);
extern void original_subtitle_mem_start(void *,const void *,u32);
extern void original_subtitle_sj_start(void *,const void *);
extern void subtitle_sync_code(u32,u32);
extern const u16 subtitle_hook_templates[][6];
typedef struct { u32 handle,bank,member,kind,serial,samples,frequency,ms,state; } Voice;
typedef struct {
    u32 magic,installed,install_error,frames,draws,last_draw_bytes,queue,mode,events;
    Voice voice[8];
    Voice ring[32];
} SubtitleDiagnostics;
volatile SubtitleDiagnostics subtitle_diagnostics;
typedef struct { u32 pointer,available;const SourceIdentity *identity; } PendingSource;
static PendingSource source_candidate[8];
static volatile u32 *output_queue;
static const u8 *halfwidth_font;
#include "voice_subtitle_hooks.h"
#define DIAG_MAGIC 0x32564253

void *memcpy(void *destination,const void *source,unsigned bytes) {
    u8 *out=destination;const u8 *in=source;
    while(bytes--) *out++=*in++;
    return destination;
}

static int ram(u32 address,unsigned bytes) {
    return address>=0x8c000000 && address<=0x8d000000-bytes;
}

#include "voice-secondary-identity.h"
#include "voice_subtitle_secondary_data.h"
static __attribute__((noinline)) void identify_secondary(unsigned index,u32 count,u32 frequency) {
    PendingSource *candidate=source_candidate+index;
    volatile Voice *v=subtitle_diagnostics.voice+index;
    const volatile u32 *sj;const SourceIdentity *identity;
    u32 object=candidate->pointer,pointer,capacity,readable,free_bytes,write_cursor,read_cursor;
    if(candidate->identity || v->bank || v->kind!=5 || !object || (object&3) || !ram(object,48)) return;
    sj=(const volatile u32 *)object;
    if(sj[0]!=0x8c14114c || sj[1]!=1) return;
    pointer=sj[7];capacity=sj[8];
    if(capacity<256 || capacity>0x1000000 || !ram(pointer,capacity)) return;
    readable=sj[3];free_bytes=sj[4];write_cursor=sj[5];read_cursor=sj[6];
    identity=secondary_match((const volatile u8 *)pointer,capacity,readable,free_bytes,
                             write_cursor,read_cursor,count,frequency,
                             secondary_identities,SECONDARY_IDENTITY_COUNT);
    /* Reject a buffer whose producer/consumer counters changed during hashing. */
    if(!identity || sj[0]!=0x8c14114c || sj[1]!=1 || sj[7]!=pointer || sj[8]!=capacity ||
       sj[3]!=readable || sj[4]!=free_bytes || sj[5]!=write_cursor || sj[6]!=read_cursor) return;
    candidate->identity=identity;v->bank=identity->bank;v->member=identity->member;
}

static u32 bank_name_hash(const volatile char *name) {
    unsigned i;u32 value=2166136261u;
    for(i=0;i<40;++i) {
        unsigned c=(u8)name[i];
        if(!c) return i?value:0;
        if(c<32 || c>126) return 0;
        if(c>='A' && c<='Z') c+=32;
        value=(value^c)*16777619u;
    }
    return 0;
}
static u32 bank_hash(unsigned slot) {
    u32 pointer;if(slot>=256) return 0;
    pointer=((volatile u32 *)0x8c19d93c)[slot];
    return ram(pointer,56)?bank_name_hash((const volatile char *)(pointer+16)):0;
}
static Voice snapshot(void *handle,u32 bank,u32 member,unsigned kind) {
    Voice v;v.handle=(u32)handle;v.bank=bank;v.member=member;v.kind=kind;
    v.serial=++subtitle_diagnostics.events;v.samples=v.frequency=v.ms=v.state=0;
    return v;
}
static int player_index(void *handle) {
    u32 offset=(u32)handle-0x8c13f040;
    return offset<0x520 && offset%0xa4==0?(int)(offset/0xa4):-1;
}
static void remember(void *handle,u32 bank,u32 member,unsigned kind) {
    Voice v;int index;unsigned alias;
    for(alias=0;alias<SUBTITLE_PHYSICAL_ALIAS_COUNT;++alias) {
        const PhysicalAlias *a=subtitle_physical_aliases+alias;
        if(bank==a->bank && member==a->member) {bank=a->logical_bank;member=a->logical_member;break;}
    }
    v=snapshot(handle,bank,member,kind);index=player_index(handle);
    if(index>=0) {
        subtitle_diagnostics.voice[index]=v;
        source_candidate[index].pointer=source_candidate[index].available=0;
        source_candidate[index].identity=0;
    }
    subtitle_diagnostics.ring[(v.serial-1)&31]=v;
}
static void identify(unsigned index) {
    PendingSource *candidate=source_candidate+index;
    volatile Voice *v=subtitle_diagnostics.voice+index;
    const volatile u8 *data;u32 pointer=candidate->pointer,a=2166136261u,b=5381;
    unsigned i;
    if(!pointer || candidate->identity) return;
    if(v->kind==5) {
        const volatile u32 *sj=(const volatile u32 *)pointer;u32 capacity;
        /* Only the Part 2 SJ ring class whose layout was read and audited.
         * Other caller-provided stream classes stay unbound.
         */
        if((pointer&3) || !ram(pointer,48) || sj[0]!=0x8c14114c || sj[1]!=1) return;
        pointer=sj[7];capacity=sj[8];
        if(capacity<SUBTITLE_IDENTITY_PREFIX_BYTES || !ram(pointer,capacity)) return;
    } else if(v->kind!=3 || candidate->available<SUBTITLE_IDENTITY_PREFIX_BYTES) return;
    if(!ram(pointer,SUBTITLE_IDENTITY_PREFIX_BYTES)) return;
    data=(const volatile u8 *)pointer;
    if(data[0]!=0x80 || data[1]!=0) return;
    for(i=0;i<SUBTITLE_IDENTITY_PREFIX_BYTES;++i) {a=(a^data[i])*16777619u;b=(b*33)^data[i];}
    for(i=0;i<SUBTITLE_IDENTITY_COUNT;++i) {
        const SourceIdentity *identity=subtitle_identities+i;
        if(a==identity->fingerprint_a && b==identity->fingerprint_b) {
            candidate->identity=identity;v->bank=identity->bank;v->member=identity->member;
            return;
        }
    }
}
void native_subtitle_stream_open(void *handle,u32 slot,u32 member) {
    remember(handle,bank_hash(slot),member,4);
    original_subtitle_stream_open(handle,slot,member);
}
void native_subtitle_afs_start(void *handle,u32 slot,u32 member) {
    remember(handle,bank_hash(slot),member,1);
    original_subtitle_afs_start(handle,slot,member);
}
void native_subtitle_fname_start(void *handle,const char *name) {
    remember(handle,ram((u32)name,40)?bank_name_hash(name):0,0,2);
    original_subtitle_fname_start(handle,name);
}
void native_subtitle_mem_start(void *handle,const void *data,u32 bytes) {
    int index;remember(handle,0,bytes,3);index=player_index(handle);
    if(index>=0) {
        source_candidate[index].pointer=(u32)data;source_candidate[index].available=bytes;
        identify(index);
    }
    original_subtitle_mem_start(handle,data,bytes);
}
void native_subtitle_sj_start(void *handle,const void *stream) {
    /* A caller-supplied stream must not inherit a previous AFS binding. */
    int index;remember(handle,0,(u32)stream,5);index=player_index(handle);
    if(index>=0) {source_candidate[index].pointer=(u32)stream;identify(index);}
    original_subtitle_sj_start(handle,stream);
}
void subtitle_init(void) {
    unsigned i,j;volatile u8 *zero=(volatile u8 *)&subtitle_diagnostics;
    if(subtitle_diagnostics.magic==DIAG_MAGIC && subtitle_diagnostics.installed==SUBTITLE_HOOK_COUNT) return;
    for(i=0;i<sizeof(subtitle_diagnostics);++i) zero[i]=0;
    zero=(volatile u8 *)source_candidate;
    for(i=0;i<sizeof(source_candidate);++i) zero[i]=0;
    subtitle_diagnostics.magic=DIAG_MAGIC;
    /* Check every prologue before changing any executable byte. */
    for(i=0;i<SUBTITLE_HOOK_COUNT;++i) {
        const SubtitleHook *h=subtitle_hooks+i;
        for(j=0;j<12;++j) if(((volatile u8 *)h->address)[j]!=h->expected[j]) {
            subtitle_diagnostics.install_error=h->address;return;
        }
    }
    /* Render from the loaded licensed font, never the BIOS/G1 bus. */
    halfwidth_font=(const u8 *)0x8c2eec80u;
    {
        u32 saved_sr,masked_sr;
        __asm__ volatile("stc sr,%0":"=r"(saved_sr));
        masked_sr=saved_sr|0xf0u;
        __asm__ volatile("ldc %0,sr"::"r"(masked_sr):"memory");
    for(i=0;i<SUBTITLE_HOOK_COUNT;++i) {
        const SubtitleHook *h=subtitle_hooks+i;volatile u16 *code=(volatile u16 *)h->address;
        for(j=0;j<6;++j) code[j]=subtitle_hook_templates[i][j];
        subtitle_sync_code(h->address,12);
        subtitle_diagnostics.installed++;
    }
        __asm__ volatile("ldc %0,sr"::"r"(saved_sr):"memory");
    }
}
static u32 divide(u32 numerator,u32 denominator) {
    u32 result=0,bit=1;
    if(!denominator) return 0;
    while(denominator<=numerator && !(denominator&0x80000000)) {denominator<<=1;bit<<=1;}
    while(bit) {if(numerator>=denominator) {numerator-=denominator;result|=bit;}denominator>>=1;bit>>=1;}
    return result;
}
static u32 milliseconds(u32 samples,u32 frequency) {
    u32 seconds=divide(samples,frequency),remainder=samples-seconds*frequency;
    return seconds*1000+divide(remainder*1000,frequency);
}
static u32 coordinate(unsigned n) {
    unsigned shift=0,value=n;if(!n) return 0;
    while(value>>=1) ++shift;
    return ((shift+127)<<23)|((n<<(23-shift))&0x7fffff);
}
static void packet(const u32 *words) {
    unsigned i;volatile u32 *sq=output_queue;
    for(i=0;i<8;++i) sq[i]=words[i];
    __asm__ volatile("pref @%0"::"r"(sq):"memory");output_queue+=8;
}
static void header(u32 color) {
    u32 h[8]={0xa2000000,0xe4000000,0x94900000,0,color,0,0,0};packet(h);
}
static void rectangle(unsigned x,unsigned y,unsigned w,unsigned h) {
    u32 z=0x49742410;
    u32 a[8]={0xf0000000,coordinate(x),coordinate(y),z,coordinate(x+w),coordinate(y),z,coordinate(x+w)};
    u32 b[8]={coordinate(y+h),z,coordinate(x),coordinate(y+h),0,0,0,0};packet(a);packet(b);
}
static int halfwidth(u16 token) {
    return token>=SUBTITLE_ASCII_BASE+0x21 && token<=SUBTITLE_ASCII_BASE+0x7e;
}
static const u8 *glyph_bitmap(u16 token,unsigned *width) {
    if(halfwidth(token)) {
        *width=12;
        return halfwidth_font+36*(token-SUBTITLE_ASCII_BASE-0x20);
    }
    *width=24;
    return (const u8 *)(0x8c2c0000+SUBTITLE_FONT_BITMAP_OFFSET+72*(token-1));
}
/* Merge equal adjacent horizontal runs. Every original font pixel is retained,
 * while a tall stem uses one rectangle instead of one per bitmap scanline. */
static int ink(const u8 *g,unsigned width,unsigned x,unsigned y) {
    unsigned n=y*width+x;return !!(g[n>>3]&(128>>(n&7)));
}
static int same_run(const u8 *g,unsigned width,unsigned y,unsigned first,unsigned last) {
    unsigned x;
    if((first && ink(g,width,first-1,y)) || (last+1<width && ink(g,width,last+1,y))) return 0;
    for(x=first;x<=last;++x) if(!ink(g,width,x,y)) return 0;
    return 1;
}
static unsigned glyph_rectangles(u16 token,unsigned ox,unsigned oy,int emit) {
    unsigned width;const u8 *g=glyph_bitmap(token,&width);
    unsigned x,y,count=0;
    for(y=0;y<24;++y) for(x=0;x<width;++x) if(ink(g,width,x,y)) {
        unsigned first=x,h=1;
        while(x+1<width && ink(g,width,x+1,y)) ++x;
        if(y && same_run(g,width,y-1,first,x)) continue;
        while(y+h<24 && same_run(g,width,y+h,first,x)) ++h;
        ++count;if(emit) rectangle(ox+first,oy+y,x-first+1,h);
    }
    return count;
}
static unsigned glyph_runs(u16 token) {return glyph_rectangles(token,0,0,0);}
static void glyph(u16 token,unsigned ox,unsigned oy) {glyph_rectangles(token,ox,oy,1);}
static void draw(const u16 *text,unsigned bottom) {
    unsigned i,lines=1,width=0,line_width=0,runs=0,x,y,bytes;u32 sr,mode,start;
    volatile u32 *lists;
    for(i=0;text[i];++i) {
        u16 c=text[i];if(c==SUBTITLE_NEWLINE) {if(line_width>width) width=line_width;line_width=0;++lines;}
        else if(c==SUBTITLE_SPACE) line_width+=12;
        else if(halfwidth(c)) {if(!halfwidth_font) return;line_width+=12;runs+=glyph_runs(c);}
        else if(c<=SUBTITLE_FONT_GLYPHS) {line_width+=24;runs+=glyph_runs(c);}
        else return;
    }
    if(line_width>width) width=line_width;
    if(width>560 || lines>3 || !width) return;
    bytes=128+runs*64;mode=*(volatile u32 *)0x8c14d7f8;
    /* The original frame closer also selects mode zero before submission. */
    ((void (*)(u32))0x8c052e1a)(0);
    lists=*(volatile u32 **)0x8c14d588;
    if(!ram((u32)lists,20)) {((void (*)(u32))0x8c052e1a)(mode);return;}
    output_queue=(volatile u32 *)lists[2];start=(u32)output_queue;
    subtitle_diagnostics.queue=start;subtitle_diagnostics.mode=mode;
    if((start&0xfe000000)!=0xe0000000 || (start&31) || lists[3]<start || lists[3]-start<bytes+32) {((void (*)(u32))0x8c052e1a)(mode);return;}
    __asm__ volatile("stc sr,%0":"=r"(sr));
    {u32 masked=sr|0xf0;__asm__ volatile("ldc %0,sr"::"r"(masked):"memory");}
    header(0x59000000);rectangle((640-width)/2-12,bottom-12-lines*28,width+24,lines*28+12);
    header(0xffffffff);x=(640-width)/2;y=bottom-6-lines*28;
    for(i=0;text[i];++i) {
        u16 c=text[i];
        if(c==SUBTITLE_NEWLINE) {x=(640-width)/2;y+=28;}
        else if(c==SUBTITLE_SPACE) x+=12;
        else {glyph(c,x,y);x+=halfwidth(c)?12:24;}
    }
    lists[2]=(u32)output_queue;subtitle_diagnostics.last_draw_bytes=(u32)output_queue-start;
    subtitle_diagnostics.draws++;
    __asm__ volatile("ldc %0,sr"::"r"(sr):"memory");
    ((void (*)(u32))0x8c052e1a)(mode);
}
void native_subtitle_frame_end(void) {
    unsigned i,j,bottom=SUBTITLE_BOX_BOTTOM;int active=0;const u16 *selected=0,*song=0;
    subtitle_diagnostics.frames++;
    /* The options byte and native lyric drawer use separate storage. Reapply
     * the selected option after save restoration/stage transitions, exactly
     * like original 8c0e55d2 -> 8c0d1732 -> 8c040494. 0=shown, 1=hidden. */
    {u8 option=*(volatile u8 *)0x8c23fb95;
     if(option<=1) *(volatile u8 *)0x8c19145c=option;}

    for(i=0;i<8;++i) {
        volatile u8 *handle=(volatile u8 *)(0x8c13f040+i*0xa4);
        volatile Voice *v=subtitle_diagnostics.voice+i;int count=0,frequency=1;
        v->state=handle[0]?handle[1]:0;
        if(handle[0] && (v->state==3 || v->state==4)) {
            unsigned mode=handle[2];
            if((mode==2 && v->kind==3) || (mode==3 && v->kind==5)) identify(i);
            if((mode==0 && v->kind!=1 && v->kind!=2) ||
               (mode==2 && v->kind!=3) || (mode==3 && v->kind!=5) ||
               (mode==4 && v->kind!=4) || (mode!=0 && mode!=2 && mode!=3 && mode!=4)) v->bank=0;
            ((void (*)(const void *,int *,int *))0x8c06917e)((const void *)handle,&count,&frequency);
            v->samples=count;v->frequency=frequency;
            if(count>=0 && frequency>=8000 && frequency<=96000) {
                v->ms=milliseconds((u32)count,(u32)frequency);active=1;
                if(mode==3 && v->kind==5) identify_secondary(i,(u32)count,(u32)frequency);
                /* Linked SJ music may append a later clip without StartSj.
                 * Its cumulative clock cannot label the original member past
                 * that member's duration. Source changes need a new binding.
                 */
                if(source_candidate[i].identity &&
                   ((u32)frequency!=source_candidate[i].identity->frequency ||
                    (u32)count>source_candidate[i].identity->samples)) v->bank=0;
                if(v->serial) {
                    volatile Voice *event=subtitle_diagnostics.ring+((v->serial-1)&31);
                    /* Preserve the last observed clock after short clips stop.
                     * Do not overwrite a ring slot already reused by a newer clip.
                     */
                    if(event->serial==v->serial) {
                        event->bank=v->bank;event->member=v->member;event->samples=count;event->frequency=frequency;
                        event->ms=v->ms;event->state=v->state;
                    }
                }
                for(j=0;j<SUBTITLE_RECORD_COUNT;++j) {
                    const Subtitle *s=subtitle_records+j;
                    if(v->bank==s->bank && v->member==s->member && v->ms>=s->start_ms && v->ms<s->end_ms) {
                        if(s->bank==0x9086675au && s->member==10) song=s->text;
                        else {selected=s->text;bottom=s->box_bottom;}
                    }
                }
            }
        } else v->samples=v->frequency=v->ms=0;
    }
#if SUBTITLE_DRAW_TEST
    if(active) {selected=subtitle_test_text;bottom=SUBTITLE_BOX_BOTTOM;}
#endif
    if(song) draw(song,464);
    if(selected) draw(selected,song && bottom>350?350:bottom);
    original_subtitle_frame_end();
}
