# ── Shared design tokens ────────────────────────────────────────────────────
BG_PAGE       = "#0f0f23"
BG_HEADER     = "#16213e"
BG_CARD       = "#1a1a3e"
BORDER_CARD   = "#2d2d5e"
BORDER_NAV    = "#2a2a4a"
ACCENT_BLUE   = "#60A5FA"
ACCENT_LOGO   = "#7B68EE"
BTN_PRIMARY   = "#3B82F6"
BTN_SUCCESS   = "#10B981"
BTN_DANGER    = "#EF4444"
TEXT_PRIMARY  = "white"
TEXT_SECONDARY = "#D1D5DB"
TEXT_MUTED    = "#6B7280"
COVER_GRADIENT = "linear-gradient(135deg, #0d1b3e 0%, #1a2a5e 40%, #16213e 100%)"
AVATAR_PLACEHOLDER = "https://ui-avatars.com/api/?background=3B82F6&color=fff&size=256&bold=true&name="

# ── Shared CSS injected on every page ───────────────────────────────────────
SHARED_CSS = f"""
    body, .q-page {{ background: {BG_PAGE} !important; }}

    .aivp-header {{
        background: {BG_HEADER};
        border-bottom: 1px solid {BORDER_NAV};
    }}

    .param-card {{
        background: {BG_CARD};
        border: 1px solid {BORDER_CARD};
        border-radius: 8px;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }}
    .param-card:hover {{
        border-color: {ACCENT_BLUE};
        box-shadow: 0 4px 20px rgba(96,165,250,0.12);
    }}

    .stat-card {{
        background: {BG_CARD};
        border: 1px solid {BORDER_CARD};
        border-radius: 8px;
        padding: 1.2rem 2rem;
        text-align: center;
        min-width: 120px;
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }}
    .stat-card:hover {{
        border-color: {ACCENT_BLUE};
        box-shadow: 0 4px 20px rgba(96,165,250,0.12);
    }}

    .run-btn {{
        background: {ACCENT_BLUE} !important;
        letter-spacing: 0.18em !important;
        transition: all 0.2s ease !important;
        font-size: 1.1rem !important;
        padding: 0.8rem 4rem !important;
        border-radius: 22px !important;
        color: white !important;
        font-weight: 700 !important;
    }}
    .run-btn:hover {{
        background: {BTN_PRIMARY} !important;
        box-shadow: 0 0 40px rgba(96,165,250,0.4) !important;
    }}

    .q-tabs {{ background: {BG_HEADER} !important; border-bottom: 1px solid {BORDER_NAV} !important; }}
    .q-tab--active .q-tab__label {{ color: {ACCENT_BLUE} !important; }}
    .q-tab--active {{ border-bottom: 2px solid {ACCENT_BLUE} !important; }}
    .q-tab__label {{ color: {TEXT_MUTED}; font-size: 0.95rem !important; }}
    .q-tabs__content, .q-tab-panels {{ background: transparent !important; }}

    .cover-wrap, .profile-cover-wrap {{ position: relative; }}
    .avatar-ring, .profile-avatar-ring {{
        border-radius: 50%; overflow: hidden;
        border: 4px solid {BG_PAGE};
        box-shadow: 0 0 0 3px rgba(96,165,250,0.4), 0 8px 28px rgba(59,130,246,0.2);
        background: {BG_CARD};
    }}
    .avatar-ring {{
        position: absolute; bottom: -52px; left: 40px;
        width: 108px; height: 108px;
    }}
    .profile-avatar-ring {{
        position: absolute; bottom: -54px; left: 48px;
        width: 112px; height: 112px;
    }}

    .photo-thumb {{
        position: relative; border-radius: 8px; overflow: hidden;
        border: 1px solid {BORDER_CARD}; transition: all 0.2s;
    }}
    .photo-thumb:hover {{ border-color: {ACCENT_BLUE}; }}
    .photo-del {{
        position: absolute; top: 4px; right: 4px;
        background: rgba(239,68,68,0.85); border-radius: 6px;
        padding: 2px 7px; font-size: 0.72rem; color: white;
        cursor: pointer; opacity: 0; transition: opacity 0.2s;
    }}
    .photo-thumb:hover .photo-del {{ opacity: 1; }}

    .profile-cover-overlay {{
        position: absolute; bottom: 0; left: 0; right: 0; height: 80px;
        background: linear-gradient(to top, {BG_PAGE} 0%, transparent 100%);
    }}

    .about-row {{ display: flex; align-items: center; gap: 12px; margin-bottom: 14px; }}
    .about-icon {{ font-size: 1rem; width: 22px; text-align: center; flex-shrink: 0; }}
    .about-label {{ color: {TEXT_MUTED}; font-size: 0.82rem; width: 110px; flex-shrink: 0; }}
    .about-value {{ color: {TEXT_SECONDARY}; font-size: 0.86rem; }}

    .recent-run-row {{
        display: flex; align-items: center; justify-content: space-between;
        padding: 10px 0; border-bottom: 1px solid {BORDER_CARD};
    }}
    .recent-run-row:last-child {{ border-bottom: none; }}

    .edit-cover-btn {{
        position: absolute; top: 14px; right: 14px;
        background: rgba(0,0,0,0.55); border: 1px solid rgba(255,255,255,0.15);
        border-radius: 8px; padding: 5px 14px; cursor: pointer;
        color: white; font-size: 0.82rem; display: flex; align-items: center; gap: 6px;
        backdrop-filter: blur(4px);
    }}

    .aivp-dialog {{
        background: {BG_CARD} !important;
        border: 1px solid {BORDER_CARD} !important;
        border-radius: 12px !important;
    }}
"""
