def calculate_trust_score(business):
    reviews = business.reviews
    if not reviews:
        return 0.0
    
    total_points = 0
    total_weight = 0
    
    for r in reviews:
        weight = 1.0 if r.is_verified_customer else 0.5
        total_points += (r.rating * weight)
        total_weight += weight
        
    base_score = total_points / total_weight
    
    # Accreditation boost
    if business.is_accredited:
        base_score = min(5.0, base_score + 0.5)
        
    return round(base_score, 1)