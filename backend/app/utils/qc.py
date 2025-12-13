def qc_status(image, inference_result):
    """
    QC based on model confidence.
    Thresholds tailored for satellite rooftop solar detection.
    """

    conf = float(inference_result.get("confidence", 0.0))

    if conf >= 0.60:
        return "VERIFIABLE"
    elif conf >= 0.35:
        return "LIKELY_SOLAR_BUT_LOW_CONFIDENCE"
    else:
        return "NOT_VERIFIABLE"
