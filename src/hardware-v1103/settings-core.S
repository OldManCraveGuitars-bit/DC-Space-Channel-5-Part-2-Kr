/* Fixed entry points keep TITLE control/display independent of core size. */
    .section .entry,"ax"
    .global _native_state_init
_native_state_init:
    mov.l 1f,r0
    jmp @r0
    nop
    nop
1:  .long _state_init
    .long 0
    .global _native_vmu_tick
_native_vmu_tick:
    mov.l 1f,r0
    jmp @r0
    nop
    nop
1:  .long _vmu_tick
    .long 0
    .global _native_vmu_changed
_native_vmu_changed:
    mov.l 1f,r0
    jmp @r0
    nop
    nop
1:  .long _vmu_changed
    .long 0
    .global _native_font_entry
_native_font_entry:
    mov.l 1f,r0
    jmp @r0
    nop
    nop
1:  .long _font_boot_uncached + 0x20000000
    .long 0

    .global _native_judgment_phase_entry
_native_judgment_phase_entry:
    mov.l 1f,r0
    jmp @r0
    nop
    nop
1:  .long _native_judgment_phase
    .long 0

    .global _native_title_entry
_native_title_entry:
    mov.l 1f,r0
    jmp @r0
    nop
    nop
1:  .long _title_boot_init
    .long 0

    .section .text
    .global _original_font_init
_original_font_init:
    mov.l r14,@-r15
    mov.l font_system,r14
    mov.l r13,@-r15
    sts.l pr,@-r15
    mov.l font_size,r3
    mov.l @(24,r14),r13
    mov.l r4,@(16,r14)
    jsr @r3
    mov r14,r4
    mov.l font_alloc,r2
    jsr @r2
    mov r0,r4
    mov.l font_create,r3
    mov.l r0,@(24,r14)
    jsr @r3
    mov r14,r4
    tst r13,r13
    bt font_done
    lds.l @r15+,pr
    mov r13,r4
    mov.l font_free,r3
    mov.l @r15+,r13
    jmp @r3
    mov.l @r15+,r14
font_done:
    lds.l @r15+,pr
    mov.l @r15+,r13
    rts
    mov.l @r15+,r14
    .global _original_font_init_end
_original_font_init_end:
    .align 2
font_system: .long 0x8c172388
font_size: .long 0x8c06b882
font_alloc: .long 0x8c063f0a
font_create: .long 0x8c016cd6
font_free: .long 0x8c063fd8

/* Keep CRI hooks out of boot/logo initialization. The patched TITLE
 * creation entry installs them before the original title object is created.
 * This runs independently of options/menu drawing or VMU availability.
 */
    .align 2
    .global _font_boot_init
_font_boot_init:
    sts.l pr,@-r15
    mov.l r4,@-r15
    mov.l boot_state_init,r0
    jsr @r0
    nop
    mov.l @r15+,r4
    lds.l @r15+,pr
    mov.l boot_font_init,r0
    jmp @r0
    nop
    .align 2
boot_state_init: .long _state_init
boot_font_init: .long _original_font_init

    .global _title_boot_init
_title_boot_init:
    sts.l pr,@-r15
    mov.l r4,@-r15
    mov.l r5,@-r15
    mov.l r6,@-r15
    mov.l r7,@-r15
    mov.l title_subtitle_init,r0
    jsr @r0
    nop
    mov.l @r15+,r7
    mov.l @r15+,r6
    mov.l @r15+,r5
    mov.l @r15+,r4
    lds.l @r15+,pr
    /* Original TITLE.BIN 8c270000..8c27000b prologue. */
    .global _original_title_init
_original_title_init:
    mov.l r14,@-r15
    sts.l pr,@-r15
    add #-8,r15
    mov.l title_create,r3
    mov.l r5,@r15
    mov.l r6,@(4,r15)
    mov.l title_resume,r0
    jmp @r0
    nop
    .align 2
title_subtitle_init: .long _subtitle_init
title_create: .long 0x8c274f14
title_resume: .long 0x8c27000c

/* The resident bootstrap has written back the entire loaded code range.
 * This entry is fetched through P2, so stale I-cache lines cannot affect it.
 * Invalidate the code's I-cache entries before the first P1 execution.
 * SH7750 cache address-array protocol; also used by _subtitle_sync_code.
 */
    .align 2
    .global _font_boot_uncached
_font_boot_uncached:
    mov.l r4,@-r15
    stc sr,r0
    mov.l r0,@-r15
    mov.l boot_irq_mask,r1
    or r1,r0
    ldc r0,sr
    mov.l boot_start,r4
    mov.l boot_end,r5
    mov.l boot_array,r1
    mov.l boot_entry_mask,r2
    mov.l boot_tag_mask,r3
boot_invalidate:
    mov r4,r6
    mov r4,r7
    and r2,r6
    or r1,r6
    and r3,r7
    mov.l r7,@r6
    add #32,r4
    cmp/hi r4,r5
    bt boot_invalidate
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    mov.l @r15+,r0
    ldc r0,sr
    mov.l @r15+,r4
    mov.l boot_ready,r0
    jmp @r0
    nop
    .align 2
boot_irq_mask: .long 0x100000f0
boot_start: .long 0x8c2f0000
boot_end: .long _payload_code_end
boot_array: .long 0xf0000000
boot_entry_mask: .long 0x1fe0
boot_tag_mask: .long 0xfffffc00
boot_ready: .long _font_boot_init

    .section .font_hook,"ax"
    /* Resident bootstrap occupies exactly the original 56-byte function.
     * Its PC is 0x8c03add6 (2 mod 4). Explicit PC-relative encodings avoid
     * increasing the input section alignment and shifting the hook.
     * Save PR/font, use the unchanged SDK writeback function, restore,
     * and tail-jump to the uncached font entry. No new code is fetched
     * before writeback completes. The original function is cloned above.
     */
    .short 0x4f22,0x2f46          /* save PR, R4 */
    .short 0xd405,0xd505,0xd006   /* start, bytes, SDK writeback */
    .short 0x400b,0x0009          /* jsr @r0; nop */
    .short 0x64f6,0x4f26          /* restore R4, PR */
    .short 0xd004,0x402b,0x0009   /* load P2 entry; jmp; nop */
    .short 0x0009                /* align literals in absolute RAM */
    .4byte 0x8c2f0000
    .4byte _payload_code_bytes
    .4byte 0x8c0163b6
    .4byte 0xac2f0030
    .rept 7
    .short 0x0009
    .endr

    .section .title_hook,"ax"
    mov.l 1f,r0
    jmp @r0
    nop
    nop
1:  .long _native_title_entry
