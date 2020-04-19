def normalize_cpf(cpf):
    if cpf:
        cpf = cpf.replace(".", "").replace("-", "")
    return cpf
