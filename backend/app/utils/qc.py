def qc_status(image, inference_result):
    """
    QC based on model confidence.
    Values from 0.35–0.6 = acceptable for rooftop solar detection on satellite images.
    """

    conf = float(inference_result.get("confidence", 0.0))

    if conf >= 0.6:
        return "VERIFIABLE"
    elif conf >= 0.35:
        return "LIKELY_SOLAR_BUT_LOW_CONFIDENCE"
    else:
        return "NOT_VERIFIABLE"
