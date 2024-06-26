import requests, ipaddress, sys, os, itertools, threading, time, concurrent.futures

def animate():
    def animate_helper():
        for cursor in itertools.cycle('|/-\\'):
            if done:
                break
            sys.stdout.write('\rPlease wait..' + cursor + '  ')
            sys.stdout.flush()
            time.sleep(0.1) 
    threading.Thread(target=animate_helper, daemon=True).start()
def get_country_ipv4_ips(country_code):
    url = f"https://stat.ripe.net/data/country-resource-list/data.json?resource={country_code}"
    response = requests.get(url)
    data = response.json()
    if 'data' in data and 'resources' in data['data']:
        resources = data['data']['resources']
        ipv4_networks = [ip for ip in resources.get('ipv4', [])]
        return ipv4_networks
    else:
        print(f"Нет данных для кода страны {country_code} или нет IPv4-ресурсов.")
        return []
def get_ipv4_for_countries(input_data):
    ipv4_per_country = {}
    if isinstance(input_data, str) and os.path.isfile(input_data): 
        with open(input_data, 'r') as file:
            country_codes = file.readlines()
        country_codes = [code.strip() for code in country_codes]
    elif isinstance(input_data, str): 
        country_codes = [input_data]
    else:
        print("Неверный формат ввода.")
        sys.exit(1)
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_country = {executor.submit(get_country_ipv4_ips, country_code): country_code for country_code in country_codes}
        for future in concurrent.futures.as_completed(future_to_country):
            country_code = future_to_country[future]
            try:
                ipv4_ips = future.result()
                ipv4_per_country[country_code] = ipv4_ips
                save_to_file(country_code, ipv4_ips)
            except Exception as exc:
                print(f"Возникла ошибка при получении данных для кода страны {country_code}: {exc}")
    return ipv4_per_country
def save_to_file(country_code, ipv4_ips):
    directory = "country"
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, f"{country_code}_CIDR.txt")
    with open(file_path, 'w') as file:
        for ipv4_ip in ipv4_ips:
            file.write(ipv4_ip + '\n')
    return file_path

if __name__ == "__main__":
    done = False
    animate()
    if len(sys.argv) != 2:
        print("Использование: python script.py <имя_файла_или_код_страны>")
        sys.exit(1)
    input_data = sys.argv[1]
    ipv4_per_country = get_ipv4_for_countries(input_data)
    done = True
    if isinstance(input_data, str) and os.path.isfile(input_data):
        current_directory = os.getcwd()
        print(f"Результаты сохранены в каталог: {current_directory}/country/")
        sys.exit()
    for country_code, ipv4_ips in ipv4_per_country.items():
        print(f"IPv4-адреса для {country_code}:")
        for ipv4_ip in ipv4_ips:
            print(ipv4_ip)
        print()
