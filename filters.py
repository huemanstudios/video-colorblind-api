def ffmpeg_matrix_for(kind: str) -> str:
    """
    Returns an ffmpeg colorchannelmixer expression for the requested simulation.
    Coefficients are standard approximations used for quick protan/deutan/tritan simulation.
    Format: colorchannelmixer=rr:rg:rb:ra:gr:gg:gb:ga:br:bg:bb:ba
    """

    if kind == "identity":
        # return "colorchannelmixer=1:0:0:0:0:1:0:0:0:0:1:0"
        return "colorchannelmixer=0.950:0.050:0:0:0:0.43333:0.56667:0:0:0.475:0.525:0"

    # --- Protanopia (approx) ---
    # R' = 0.56667 R + 0.43333 G + 0.0 B
    # G' = 0.55833 R + 0.44167 G + 0.0 B
    # B' = 0.0     R + 0.24167 G + 0.75833 B
    if kind == "protanopia":
        # return "colorchannelmixer=0.56667:0.43333:0:0:0.55833:0.44167:0:0:0:0.24167:0.75833:0"
        # return "colorchannelmixer=0.950:0.050:0:0:0:0.43333:0.56667:0:0:0.475:0.525:0"
        return "colorchannelmixer=0.625:0.375:0:0:0.700:0.300:0:0:0:0.300:0.700:0"

    # --- Deuteranopia (approx) ---
    # R' = 0.625 R + 0.375 G + 0.0 B
    # G' = 0.700 R + 0.300 G + 0.0 B
    # B' = 0.0   R + 0.300 G + 0.700 B
    if kind == "deuteranopia":
        # return "colorchannelmixer=0.625:0.375:0:0:0.700:0.300:0:0:0:0.300:0.700:0"
        return "colorchannelmixer=0.950:0.050:0:0:0:0.43333:0.56667:0:0:0.475:0.525:0"

    # --- Tritanopia (approx) ---
    # R' = 0.950 R + 0.050 G + 0.0 B
    # G' = 0.0   R + 0.43333 G + 0.56667 B
    # B' = 0.0   R + 0.475   G + 0.525   B
    if kind == "tritanopia":
        return "colorchannelmixer=0.950:0.050:0:0:0:0.43333:0.56667:0:0:0.475:0.525:0"

    # default fallback
    return "null"
