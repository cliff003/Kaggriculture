"""Line icons drawn on a 24 x 24 grid (stroke only), our own drawings for the figures."""

ICONS = {
    # stacked sheets
    "layers": '<path d="M12 3 2.5 8 12 13l9.5-5z"/><path d="M2.5 12.5 12 17.5l9.5-5"/><path d="M2.5 17 12 22l9.5-5"/>',
    # numbered list
    "list": '<path d="M10 6h11M10 12h11M10 18h11"/><path d="M4 4.5h1.5V9"/><path d="M3.5 13.2c.4-.9 2.6-1 2.6.3 0 1-2.6 2-2.6 3.3h2.8"/>'
            '<path d="M3.6 19.5h2.6"/>',
    # wrench
    "wrench": '<path d="M14.7 6.3a4 4 0 0 0 5 5L21 10a5.5 5.5 0 0 1-7.2-7.2L12.4 4.2a4 4 0 0 0 2.3 2.1z"/>'
              '<path d="M13.6 9.4 4 19a1.8 1.8 0 0 0 2.6 2.6l9.6-9.6"/>',
    # wheat ear
    "wheat": '<path d="M12 22V8"/><path d="M12 8c-2.2 0-3.5-1.6-3.5-3.8C10.7 4.2 12 5.8 12 8z"/>'
             '<path d="M12 8c2.2 0 3.5-1.6 3.5-3.8C13.3 4.2 12 5.8 12 8z"/>'
             '<path d="M12 13c-2.4 0-3.8-1.7-3.8-4C10.6 9 12 10.7 12 13z"/>'
             '<path d="M12 13c2.4 0 3.8-1.7 3.8-4C13.4 9 12 10.7 12 13z"/>'
             '<path d="M12 18c-2.4 0-3.8-1.7-3.8-4 2.4 0 3.8 1.7 3.8 4z"/>'
             '<path d="M12 18c2.4 0 3.8-1.7 3.8-4-2.4 0-3.8 1.7-3.8 4z"/>',
    # two arrows in a loop
    "repeat": '<path d="m17 2 3 3-3 3"/><path d="M4 11V9a4 4 0 0 1 4-4h12"/><path d="m7 22-3-3 3-3"/>'
              '<path d="M20 13v2a4 4 0 0 1-4 4H4"/>',
    # shield with tick
    "shield": '<path d="M12 2.5 20 6v6c0 5-3.6 8.6-8 9.5C7.6 20.6 4 17 4 12V6z"/><path d="m8.5 12 2.5 2.5 4.5-5"/>',
    # crescent moon
    "moon": '<path d="M20.5 14.5A8.5 8.5 0 1 1 9.5 3.5a6.6 6.6 0 0 0 11 11z"/>',
    # eye
    "eye": '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    # shop front
    "store": '<path d="M3 9.5 4.5 4h15L21 9.5"/><path d="M3 9.5a3 3 0 0 0 6 0 3 3 0 0 0 6 0 3 3 0 0 0 6 0"/>'
             '<path d="M4.5 12v8h15v-8"/><path d="M9.5 20v-5h5v5"/>',
    # sprout
    "sprout": '<path d="M12 21v-9"/><path d="M12 12C12 7.5 8.5 5 4 5c0 4.5 3.5 7 8 7z"/>'
              '<path d="M12 14c0-3.6 2.8-6 7-6 0 3.6-2.8 6-7 6z"/>',
    # flag
    "flag": '<path d="M5 21V4"/><path d="M5 4h11l-2 4 2 4H5"/>',
    # trophy / medal
    "medal": '<circle cx="12" cy="15" r="5.5"/><path d="M8.5 10.5 6 3h4l2 5 2-5h4l-2.5 7.5"/>',
    # chart going down
    "trend_down": '<path d="m3 7 6 6 4-4 8 8"/><path d="M15 17h6v-6"/>',
    # database / replays
    "db": '<ellipse cx="12" cy="5" rx="8" ry="2.8"/><path d="M4 5v14c0 1.5 3.6 2.8 8 2.8s8-1.3 8-2.8V5"/>'
          '<path d="M4 12c0 1.5 3.6 2.8 8 2.8s8-1.3 8-2.8"/>',
    # cpu / chip for learned policy
    "net": '<circle cx="5" cy="6" r="2"/><circle cx="5" cy="18" r="2"/><circle cx="19" cy="12" r="2"/>'
           '<circle cx="12" cy="6" r="2"/><circle cx="12" cy="18" r="2"/><path d="M7 6h3M7 18h3M14 6l3.4 4.8M14 18l3.4-4.8"/>',
}


def icon(name, color, size=32, stroke=2.0):
    d = ICONS[name]
    sw = stroke * 24 / size
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" '
            f'stroke-width="{sw:.2f}" stroke-linecap="round" stroke-linejoin="round" style="display:block">{d}</svg>')
