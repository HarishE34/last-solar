# app/utils/qc.py
def qc_status(image, inference_result):
    conf = float(inference_result.get("confidence", 0.0))
    if conf >= 0.7:
        return "VERIFIABLE"
    return "NOT_VERIFIABLE"
