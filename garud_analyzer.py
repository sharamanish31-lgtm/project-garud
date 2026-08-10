import re

def analyze_threat_vector(payload_string):
    """
    Heuristic scoring engine to analyze automated attack vectors
    Generates dynamic 8-dimensional structural array for vector layout
    """
    # Defensive lower-case normalization to beat mixed-case anomalies (sElEcT)
    normalized = str(payload_string).lower()
    
    # 1. Base Multi-Signature Patterns Detection
    sqli_match = len(re.findall(r"(union|select|insert|delete|drop|where|or\s+1\s*=\s*1|--|')", normalized))
    xss_match = len(re.findall(r"(<script|script>|javascript:|onerror=|onload=|alert\()", normalized))
    traversal_match = len(re.findall(r"(\.\.\/|\.\.\\|etc/passwd|/boot\.ini|win\.ini)", normalized))
    rce_match = len(re.findall(r"(wget|curl|chmod|chown|/bin/bash|/bin/sh|eval\()", normalized))
    
    # Calculate relative structural density
    total_hits = sqli_match + xss_match + traversal_match + rce_match
    
    # 2. Dynamic 8-Dimensional Feature Layout Calculation
    # Normalizing weights between 0.0 and 1.0 for Vector Database indexing
    v1_sqli = min(1.0, sqli_match * 0.25)
    v2_xss = min(1.0, xss_match * 0.25)
    v3_traversal = min(1.0, traversal_match * 0.25)
    v4_rce = min(1.0, rce_match * 0.25)
    v5_anomaly_density = min(1.0, total_hits * 0.15)
    v6_payload_len_weight = min(1.0, len(normalized) / 2000.0)
    v7_is_malicious = 1.0 if total_hits > 0 else 0.0
    v8_confidence_index = min(1.0, 0.5 + (total_hits * 0.1))
    
    calculated_vector = [v1_sqli, v2_xss, v3_traversal, v4_rce, v5_anomaly_density, v6_payload_len_weight, v7_is_malicious, v8_confidence_index]
    
    # Return structured intelligence summary
    return {
        "vector": calculated_vector,
        "classification": "malicious" if total_hits > 0 else "neutral",
        "severity_score": total_hits
    }
