import requests, ipaddress, sys, os, itertools, threading, time

def animate():
    for cursor in itertools.cycle('|/-\\'):
        if done:
            break
        sys.stdout.write('\rPlease wait..'+ cursor+'  ')
        sys.stdout.flush()
        time.sleep(0.1)

def get_country_ipv4_ips(country_code):
    url = f"https://stat.ripe.net/data/country-resource-list/data.json?resource={country_code}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if 'data' in data and 'resources' in data['data']:
            resources = data['data']['resources']
            ipv4_networks = [ip for ip in resources.get('ipv4', [])]
            return ipv4_networks
        else:
            print(f"Нет данных для кода страны {country_code} или нет IPv4-ресурсов.")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к Ripe API: {e}")
        return []

def validate_iso_code(country_code):

    if not country_code or len(country_code) != 2:
        return False
    if not country_code.isalpha():
        return False
    return True

def get_ipv4_for_countries(input_data):
    ipv4_per_country = {}
    if isinstance(input_data, str) and os.path.isfile(input_data): 
        try:
            with open(input_data, 'r') as file:
                country_codes = file.readlines()
            country_codes = [code.strip() for code in country_codes if code.strip()]
        except Exception as e:
            print(f"Ошибка чтения файла: {e}")
            sys.exit(1)
    elif isinstance(input_data, str): 
        country_codes = [input_data]
    else:
        print("Неверный формат ввода.")
        sys.exit(1)
        
    animation_thread = threading.Thread(target=animate)
    animation_thread.start()
    
    for country_code in country_codes:
        if not validate_iso_code(country_code):
            print(f"Некорректный код страны: {country_code}")
            continue
            
        ipv4_ips = get_country_ipv4_ips(country_code)
        if not ipv4_ips:
            continue
        ipv4_per_country[country_code] = ipv4_ips
        save_to_file(country_code, ipv4_ips)
        
    global done
    done = True
    animation_thread.join()
    
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
    if len(sys.argv) != 2:
        print("Использование: python script.py <имя_файла_или_код_страны>")
        sys.exit(1)

    input_data = sys.argv[1]
    ipv4_per_country = get_ipv4_for_countries(input_data)
    
    if isinstance(input_data, str) and os.path.isfile(input_data):
        current_directory = os.getcwd()
        print(f"Результаты сохранены в каталог: {current_directory}/country/")
        sys.exit()
    
    for country_code, ipv4_ips in ipv4_per_country.items():
        print(f"IPv4-адреса для {country_code}:")
        for ipv4_ip in ipv4_ips:
            print(ipv4_ip)
        print()
