def build_search_params(parsed_data):
    q_parts = []
    # Дүүрэг байвал оруулна
    if parsed_data["districts"]:
        q_parts.extend(parsed_data["districts"])
    # Өрөөний тоо байвал "X өрөө" гэж оруулна
    if parsed_data["rooms"]:
        q_parts.append(f"{parsed_data['rooms']} өрөө")
    # Үнэ (сая төгрөгөөр) нэмэх боломжтой (зөвхөн q-д орно гэж үзвэл)
    # price-г хайлтад шууд ашиглах нөхцөлөө өөрчлөх хэрэгтэй байж магадгүй
    # Жишээ: price нь хайлтын "q"-д хамаарахгүй байж болох учир одоогоор оруулахгүй

    params = {
        "q": q_parts,
        "paging": 1
    }
    return params