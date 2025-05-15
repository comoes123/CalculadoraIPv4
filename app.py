from flask import Flask, render_template, request
import ipaddress

app = Flask(__name__)

 
def is_private(ip):
    return ip.is_private

def get_ip_class(ip):
    first_octet = int(ip.exploded.split('.')[0])
    if first_octet < 128:
        return 'A'
    elif first_octet < 192:
        return 'B'
    elif first_octet < 224:
        return 'C'
    elif first_octet < 240:
        return 'D (Multicast)'
    else:
        return 'E (Experimental)'

def generar_binario_coloreado(ip_str, mask_str):
    ip = ipaddress.IPv4Address(ip_str)
    net = ipaddress.IPv4Network(f"{ip_str}/{mask_str}", strict=False)
    
    ip_bin = ''.join([f'{int(octeto):08b}' for octeto in ip_str.split('.')])
    mask = net.prefixlen

    red_bits = ip_bin[:mask]
    host_bits = ip_bin[mask:]

    # Agrupar los bits en octetos para formateo visual
    full_bin = red_bits + host_bits
    formatted = ""
    for i in range(0, len(full_bin), 8):
        chunk = full_bin[i:i+8]
        if i < mask:
            if i + 8 <= mask:
                formatted += f"<span class='red'>{chunk}</span>"
            else:
                subred = mask - i
                formatted += f"<span class='red'>{chunk[:subred]}</span><span class='green'>{chunk[subred:]}</span>"
        else:
            formatted += f"<span class='green'>{chunk}</span>"
        if i + 8 < len(full_bin):
            formatted += "."

    return formatted

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        try:
            ip_str = request.form['ip']
            mask_str = request.form['mask']
            
            network = ipaddress.IPv4Network(f"{ip_str}/{mask_str}", strict=False)
            network_ip = network.network_address
            broadcast_ip = network.broadcast_address
            usable_ips = network.num_addresses - 2 if network.num_addresses > 2 else 0
            first_usable = network.network_address + 1 if network.num_addresses > 2 else None
            last_usable = network.broadcast_address - 1 if network.num_addresses > 2 else None
            ip_class = get_ip_class(network_ip)
            private_public = "Privada" if is_private(network_ip) else "Pública"
            binary_colored = generar_binario_coloreado(ip_str, mask_str)

            return render_template('index.html', 
                                 network_ip=network_ip,
                                 broadcast_ip=broadcast_ip,
                                 usable_ips=usable_ips,
                                 first_usable=first_usable,
                                 last_usable=last_usable,
                                 ip_class=ip_class,
                                 private_public=private_public,
                                 original_ip=ip_str,
                                 original_mask=mask_str,
                                 binary_colored=binary_colored)
        except ValueError as e:
            error = f"Error: {str(e)}"
            return render_template('index.html', error=f"Error en la IP o máscara: {str(e)}")
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
