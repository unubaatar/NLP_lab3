def build_search_params(parsed_data):
    q_parts = []
    # Дүүрэг байгаа тохиолдолд:
    if parsed_data["districts"]:
        q_parts.extend(parsed_data["districts"])
    # Өрөөний тоо байвал:"X өрөө" гэж оруулна
    if parsed_data["rooms"]:
        q_parts.append(f"{parsed_data['rooms']} өрөө")
    # Үнэ (сая төгрөгөөр) нэмэх боломжтой (зөвхөн q-д орно гэж үзвэл)
    params = {
        "q": q_parts,
        "paging": 1
    }
    return params