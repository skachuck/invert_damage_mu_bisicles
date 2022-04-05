def linear_dam_mu(dam, *etc):
    mu = (dam - 0.5)/(1 - 0.5)
    mu *= (1-0.35)
    mu = 1 - mu
    mu = 1.07*min(max(mu, 0), 1)
    return mu



