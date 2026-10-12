SECTIONS {
 .subtitle_extra 0x8c2e5e70 : { *(.subtitle_extra) }
 .entry 0x8c2f0000 : { *(.entry) }
 .text 0x8c2f0100 : { *(.text*) *(.rodata*) }
 .data ALIGN(4) : { *(.data*) }
 _payload_code_end = .;
 _payload_code_bytes = _payload_code_end - 0x8c2f0000;
 .bss ALIGN(4) : { *(.bss*) *(COMMON) }
 _settings_core_end = .;
 .title_hook 0x8c270000 : { *(.title_hook) }
 .font_hook 0x8c03add6 : { *(.font_hook) }
 .judgment_hook 0x8c03bbde : { *(.judgment_hook) }
 /DISCARD/ : { *(.comment*) *(.note*) *(.eh_frame*) }
}
PROVIDE(_native_state = 0x8c2a0000);
PROVIDE(_judgment_phase_diagnostics = 0x8c2a1000);
