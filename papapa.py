import json
from prettytable import PrettyTable
import os
import time
import pwinput

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def press_enter():
    input("Tekan enter untuk lanjut")

# ==============================================================================
#                                     JSON
# ==============================================================================

def read_json_file(filename, default_data=None):
    if not os.path.exists(filename):
        if default_data is not None:
            with open(filename, 'w') as f:
                json.dump(default_data, f, indent=4)
        return default_data or []
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        return data
    except (json.JSONDecodeError, ValueError):
        print(f"File {filename} korup. Reset ke default.")
        if default_data is not None:
            with open(filename, 'w') as f:
                json.dump(default_data, f, indent=4)
        return default_data or []

def write_json_file(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
def read_antrian():
    return read_json_file('data_antrian.json', [])
def save_antrian(data):
    write_json_file('data_antrian.json', data)
def read_customers():
    return read_json_file('data_akun.json', [])
def save_customers(customers):
    write_json_file('data_akun.json', customers)
def read_saldo():
    return read_json_file('data_saldo.json', {"saldo": 0})
def save_saldo(saldo):
    write_json_file('data_saldo.json', saldo)
def read_struk():
    return read_json_file('data_struk.json', [])
def save_struk(struk):
    write_json_file('data_struk.json', struk)
def read_pending():
    return read_json_file('data_pending.json', [])
def save_pending(pending):
    write_json_file('data_pending.json', pending)
def generate_order_id():
    data = read_antrian()
    pending = read_pending()
    all_items = data + pending
    existing_ids = [item.get("ID Pemesanan", 0) for item in all_items if isinstance(item, dict)]
    return max(existing_ids) + 1 if existing_ids else 1

def create_receipt(customer, service, cost, payment_time):
    if not isinstance(customer, dict) or not isinstance(service, dict):
        print("Data customer atau service tidak valid.")
        return
    receipt_text = f"""
+================================================================================+
|        /         /           Struk Pembayaran               \          \       |
+================================================================================+
 Nama Customer    : {customer.get('username', 'N/A')}                            
 Nomor Antrian    : {service.get('Nomor Antrian', 'N/A')}                        
 Keluhan          : {service.get('Keluhan', 'N/A')}                              
 Biaya Layanan    : Rp.{cost:,.0f}                                               
 Waktu Pembayaran : {payment_time}                                               
 Status           : Dibayar                                                      
+================================================================================+
|       /     /    Terima kasih telah menggunakan layanan kami      \      \     |
+================================================================================+
"""
    print(receipt_text)
    receipt_data = {
        "Nama Customer": customer.get('username', 'N/A'),
        "Nomor Antrian": service.get('Nomor Antrian', 'N/A'),
        "Keluhan": service.get('Keluhan', 'N/A'),
        "Biaya Layanan": cost,
        "Waktu Pembayaran": payment_time,
        "Status": "Dibayar"
    }
    receipts = read_struk()
    receipts.append(receipt_data)
    save_struk(receipts)
    print("Struk Pembayaran Berhasil Dibuat.")
    press_enter()
    clear_screen()

# ==============================================================================
#                               SIGN UP & LOGIN
# ==============================================================================

def signup():
    customers = read_customers()
    username = input("Username: ").strip()
    if not username:
        print("Username tidak boleh kosong.")
        return
    if not username.isalpha():
        print("Username harus berupa huruf.")
        return
    if any(c.get("username") == username for c in customers if isinstance(c, dict)):
        print("Username sudah ada.")
        return
    password = pwinput.pwinput("Password: ")
    if not password.strip():
        print("Password tidak boleh kosong.")
        return
    if not (8 <= len(password) <= 12):
        print("Password harus 8-12 karakter.")
        return
    pin = pwinput.pwinput("PIN (4 digit): ")
    if not (pin.isdigit() and len(pin) == 4):
        print("PIN harus 4 digit angka.")
        return

    customers.append({
        "username": username,
        "password": password,
        "saldo": 0,
        "pin": pin,
    })
    save_customers(customers)
    print("Berhasil didaftarkan.")

def login():
    role_table = PrettyTable()
    role_table.title = "PILIH ROLE"
    role_table.field_names = ["No", "Role"]
    role_table.add_row(["1", "Admin"])
    role_table.add_row(["2", "Customer"])
    print(role_table)
    role_choice = input("Pilih [1-2]: ").strip()
    if role_choice == "1":
        target_role = "admin"
        accounts = [
            {"username": "admin", "password": "admin1234", "role": "admin"},
            {"username": "adminn", "password": "admin2345", "role": "admin"}
        ]
    elif role_choice == "2":
        target_role = "customer"
        accounts = read_customers()
        if not accounts:
            accounts = [{
                "username": "customer",
                "password": "customer",
                "saldo": 0,
                "pin": "1234",
                "nama": "Default Customer",
                "no_hp": "081234567890"
            }]
            save_customers(accounts)
    else:
        print("Pilihan tidak valid.")
        return None

    attempts = 0
    max_attempts = 3
    while attempts < max_attempts:
        username = input("Username: ").strip()
        password = pwinput.pwinput("Password: ")
        clear_screen()
        for acc in accounts:
            if isinstance(acc, dict) and acc.get("username") == username and acc.get("password") == password:
                return target_role, username
        attempts += 1
        print(f"Username atau password salah. ({attempts}/{max_attempts})")
    print("Terlalu banyak percobaan. Kembali ke menu utama.")
    return None

# ==============================================================================
#                               TAMPILAN MENU
# ==============================================================================

def main_app(role, username):
    clear_screen()
    print(f"Selamat datang, {username}")
    try:
        while True:
            data = read_antrian()
            menu_table = PrettyTable()
            menu_table.title = "MENU UTAMA"
            menu_table.field_names = ["No", "Menu"]

            if role == "admin":
                menu_items = [
                    ("1", "Tambah Pesanan                "),
                    ("2", "Lihat Antrian                 "),
                    ("3", "Perbarui Data Layanan Service "),
                    ("4", "Hapus Data Antrian            "),
                    ("5", "Lihat Customers               "),
                    ("6", "Perbarui Status Pembayaran    "),
                    ("7", "Terima Pesanan Baru           "),
                    ("8", "Keluar                        ")
                ]
                for no, menu in menu_items:
                    menu_table.add_row([no, menu])
                print(menu_table)
                choice = input("Pilih menu [1-8]: ").strip()
                clear_screen()
            else:
                menu_items = [
                    ("1", "Pesan Layanan"),
                    ("2", "Lihat Antrian"),
                    ("3", "Bayar Layanan"),
                    ("4", "Cek Saldo    "),
                    ("5", "Top Up Saldo "),
                    ("6", "Keluar       ")
                ]
                for no, menu in menu_items:
                    menu_table.add_row([no, menu])
                print(menu_table)
                choice = input("Pilih menu [1-6]: ").strip()
                clear_screen()

            # ======================================================================
            #                               ADMIN MENU
            # ======================================================================
            if role == "admin":
                if choice == "1":
                    name = input("Masukkan nama: ").strip()
                    while not name or not all(c.isalpha() or c.isspace() for c in name):
                        print("Nama tidak boleh kosong dan hanya boleh huruf")
                        name = input("Masukkan nama: ").strip()
                    phone = input("Masukkan No HP (11-13 digit): ")
                    while not (phone.isdigit() and 11 <= len(phone) <= 13):
                        print("No HP harus berupa angka, 11-13 digit")
                        phone = input("Masukkan No HP: ")
                    address = input("Masukkan Alamat: ").strip()
                    while not address:
                        print("Alamat tidak boleh kosong.")
                        address = input("Masukkan Alamat: ").strip()
                    complaint = input("Masukkan Keluhan: ").strip()
                    while not complaint:
                        print("Keluhan tidak boleh kosong.")
                        complaint = input("Masukkan Keluhan: ").strip()

                    valid_queues = [item.get("Nomor Antrian", 0) for item in data if isinstance(item, dict) and isinstance(item.get("Nomor Antrian"), int)]
                    queue_num = max(valid_queues) + 1 if valid_queues else 1
                    reg_time = time.strftime("%Y-%m-%d %H:%M:%S")
                    data.append({
                        "Nama": name,
                        "No HP": phone,
                        "Alamat": address,
                        "Nomor Antrian": queue_num,
                        "Keluhan": complaint,
                        "Waktu Daftar": reg_time,
                        "Status": "Menunggu",
                        "Biaya": 0,
                        "Status Pembayaran": "Belum Dibayar",
                        "Username": username
                    })
                    save_antrian(data)
                    print(f"Data berhasil ditambahkan. Nomor Antrian: {queue_num}")
                    press_enter()
                    clear_screen()

                elif choice == "2":
                    if not data:
                        print("Daftar antrian kosong.")
                        press_enter()
                        clear_screen()
                        continue
                    queue_table = PrettyTable()
                    queue_table.title = "=== Daftar Antrian ==="
                    queue_table.field_names = ["No Antrian", "Nama", "No HP", "Alamat", "Keluhan", "Status", "Biaya", "Pembayaran", "Waktu"]
                    for item in data:
                        if not isinstance(item, dict): continue
                        queue_table.add_row([
                            item.get("Nomor Antrian", "N/A"),
                            item.get("Nama", "N/A"),
                            item.get("No HP", "N/A"),
                            item.get("Alamat", "N/A"),
                            item.get("Keluhan", "N/A"),
                            item.get("Status", "N/A"),
                            f"Rp.{item.get('Biaya', 0):,.0f}",
                            item.get("Status Pembayaran", "N/A"),
                            item.get("Waktu Daftar", "N/A")
                        ])
                    print(queue_table)
                    press_enter()
                    clear_screen()

                elif choice == "3":
                    active_queues = [item for item in data if isinstance(item, dict) and item.get("Nomor Antrian") is not None]
                    if not active_queues:
                        print("Tidak ada antrian aktif yang bisa diperbarui.")
                        continue
                    print("\n--- Antrian Aktif ---")
                    temp_table = PrettyTable()
                    temp_table.field_names = ["Nomor Antrian", "Nama", "Status"]
                    for item in active_queues:
                        temp_table.add_row([item.get("Nomor Antrian", "N/A"), item.get("Nama", "N/A"), item.get("Status", "N/A")])
                    print(temp_table)
                    try:
                        queue_to_update = int(input("Masukkan Nomor Antrian yang ingin diperbarui statusnya: "))
                    except ValueError:
                        print("Input harus angka")
                        continue
                    clear_screen()

                    status_table = PrettyTable()
                    status_table.title = "PILIH STATUS BARU"
                    status_table.field_names = ["No", "Status"]
                    status_table.add_row(["1", "Menunggu"])
                    status_table.add_row(["2", "Diproses"])
                    status_table.add_row(["3", "Selesai"])
                    print(status_table)
                    status_choice = input("Pilih status baru [1-3]: ").strip()
                    clear_screen()

                    status_map = {"1": "Menunggu", "2": "Diproses", "3": "Selesai"}
                    if status_choice not in status_map:
                        print("Pilihan tidak valid.")
                        continue
                    new_status = status_map[status_choice]

                    found = False
                    for item in data:
                        if isinstance(item, dict) and item.get("Nomor Antrian") == queue_to_update:
                            item["Status"] = new_status
                            if new_status == "Selesai":
                                while True:
                                    try:
                                        cost = float(input("Masukkan Biaya Layanan: "))
                                        if cost < 0:
                                            print("Biaya tidak boleh negatif.")
                                            continue
                                        item["Biaya"] = cost
                                        break
                                    except ValueError:
                                        print("Biaya harus berupa angka.")
                            found = True
                            break
                    if found:
                        save_antrian(data)
                        print(f"Status Antrian {queue_to_update} berhasil diupdate menjadi '{new_status}'.")
                    else:
                        print(f"Nomor Antrian {queue_to_update} tidak ditemukan.")

                elif choice == "4":
                    if not data:
                        print("Tidak ada data untuk dihapus.")
                        continue
                    delete_table = PrettyTable()
                    delete_table.field_names = ["No Antrian", "Nama", "Status"]
                    for item in data:
                        if isinstance(item, dict):
                            delete_table.add_row([item.get("Nomor Antrian", "N/A"), item.get("Nama", "N/A"), item.get("Status", "N/A")])
                    print(delete_table)
                    try:
                        queue_to_delete = int(input("Nomor Antrian yang dihapus: "))
                    except ValueError:
                        print("Input harus angka")
                        continue
                    for i, item in enumerate(data):
                        if isinstance(item, dict) and item.get("Nomor Antrian") == queue_to_delete:
                            del data[i]
                            save_antrian(data)
                            print(f"Antrian {queue_to_delete} dihapus.")
                            break
                    else:
                        print(f"Antrian {queue_to_delete} tidak ditemukan.")

                elif choice == "5":
                    customers = read_customers()
                    if not customers:
                        print("Belum ada customer terdaftar.")
                        continue
                    customer_table = PrettyTable()
                    customer_table.field_names = ["Username"]
                    for c in customers:
                        if isinstance(c, dict):
                            customer_table.add_row([c.get("username", "N/A")])
                    print(customer_table)
                    press_enter()
                    clear_screen()

                elif choice == "6":
                    completed_services = [item for item in data if isinstance(item, dict) and item.get("Status") == "Selesai"]
                    if not completed_services:
                        print("Tidak ada layanan selesai.")
                        continue
                    payment_table = PrettyTable()
                    payment_table.field_names = ["No Antrian", "Nama", "Keluhan", "Status Pembayaran"]
                    for item in completed_services:
                        payment_table.add_row([
                            item.get("Nomor Antrian", "N/A"),
                            item.get("Nama", "N/A"),
                            item.get("Keluhan", "N/A"),
                            item.get("Status Pembayaran", "N/A")
                        ])
                    print(payment_table)
                    try:
                        queue_num = int(input("Nomor Antrian (0 untuk batal): "))
                    except ValueError:
                        print("Input harus angka")
                        continue
                    if queue_num == 0:
                        continue
                    service = next((item for item in completed_services if item.get("Nomor Antrian") == queue_num), None)
                    if not service:
                        print("Antrian tidak ditemukan.")
                        continue
                    payment_status_table = PrettyTable()
                    payment_status_table.field_names = ["No", "Status"]
                    payment_status_table.add_row(["1", "Belum Dibayar"])
                    payment_status_table.add_row(["2", "Terbayar"])
                    print(payment_status_table)
                    payment_choice = input("Status baru [1-2]: ").strip()
                    if payment_choice == "1":
                        service["Status Pembayaran"] = "Belum Dibayar"
                    elif payment_choice == "2":
                        service["Status Pembayaran"] = "Terbayar"
                    else:
                        print("Pilihan tidak valid.")
                        continue
                    save_antrian(data)
                    print(f"Status pembayaran antrian {queue_num} diperbarui.")

                elif choice == "7":
                    pending = read_pending()
                    if not pending:
                        print("Tidak ada pesanan pending.")
                        continue
                    pending_table = PrettyTable()
                    pending_table.field_names = ["ID", "Nama", "No HP", "Alamat", "Keluhan", "Username", "Waktu"]
                    for item in pending:
                        if isinstance(item, dict):
                            pending_table.add_row([
                                item.get("ID Pemesanan", "N/A"),
                                item.get("Nama", "N/A"),
                                item.get("No HP", "N/A"),
                                item.get("Alamat", "N/A"),
                                item.get("Keluhan", "N/A"),
                                item.get("Username", "N/A"),
                                item.get("Waktu Daftar", "N/A")
                            ])
                    print(pending_table)
                    try:
                        order_id = int(input("ID Pesanan (0 untuk batal): "))
                    except ValueError:
                        print("ID harus angka")
                        continue
                    if order_id == 0:
                        continue
                    order = next((p for p in pending if isinstance(p, dict) and p.get("ID Pemesanan") == order_id), None)
                    if not order:
                        print("ID tidak ditemukan.")
                        continue
                    action_table = PrettyTable()
                    action_table.title = "PILIH AKSI"
                    action_table.field_names = ["No", "Aksi"]
                    action_table.add_row(["1", "Terima"])
                    action_table.add_row(["2", "Tolak"])
                    print(action_table)
                    action_choice = input("Pilih aksi [1-2]: ").strip()
                    if action_choice == "1":
                        valid_queues = [item.get("Nomor Antrian", 0) for item in data if isinstance(item, dict) and isinstance(item.get("Nomor Antrian"), int)]
                        queue_num = max(valid_queues) + 1 if valid_queues else 1
                        data.append({
                            "Nama": order["Nama"],
                            "No HP": order["No HP"],
                            "Alamat": order["Alamat"],
                            "Nomor Antrian": queue_num,
                            "ID Pemesanan": order["ID Pemesanan"],
                            "Keluhan": order["Keluhan"],
                            "Waktu Daftar": order["Waktu Daftar"],
                            "Status": "Menunggu",
                            "Biaya": 0,
                            "Status Pembayaran": "Belum Dibayar",
                            "Username": order["Username"],
                            "Waktu Diterima": time.strftime("%Y-%m-%d %H:%M:%S")
                        })
                        pending.remove(order)
                        save_antrian(data)
                        save_pending(pending)
                        print(f"Pesanan ID {order_id} diterima. Nomor Antrian: {queue_num}")
                    elif action_choice == "2":
                        pending.remove(order)
                        save_pending(pending)
                        print(f"Pesanan ID {order_id} ditolak.")
                    else:
                        print("Pilihan tidak valid.")

                elif choice == "8":
                    break
                else:
                    print("Pilihan tidak valid!")

            # ======================================================================
            #                               CUSTOMER MENU
            # ======================================================================
            else:
                if choice == "1":
                    pending = read_pending()
                    active_orders = [item for item in data if isinstance(item, dict) and item.get("Username") == username and item.get("Status") not in ["Selesai", "Rejected"]]
                    active_orders += [item for item in pending if isinstance(item, dict) and item.get("Username") == username]
                    if active_orders:
                        print("Anda sudah memiliki pesanan aktif atau pending.")
                        continue
                    name = input("Nama: ").strip()
                    while not name or not all(c.isalpha() or c.isspace() for c in name):
                        print("Nama tidak valid.")
                        name = input("Nama: ").strip()
                    phone = input("No HP (11-13 digit): ")
                    while not (phone.isdigit() and 11 <= len(phone) <= 13):
                        print("No HP harus 11-13 digit angka.")
                        phone = input("No HP: ")
                    address = input("Alamat: ").strip()
                    while not address:
                        print("Alamat tidak boleh kosong.")
                        address = input("Alamat: ").strip()
                    complaint = input("Keluhan: ").strip()
                    while not complaint:
                        print("Keluhan tidak boleh kosong.")
                        complaint = input("Keluhan: ").strip()
                    pending.append({
                        "Nama": name,
                        "No HP": phone,
                        "Alamat": address,
                        "Nomor Antrian": None,
                        "ID Pemesanan": generate_order_id(),
                        "Keluhan": complaint,
                        "Waktu Daftar": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "Status": "Belum diterima",
                        "Biaya": 0,
                        "Status Pembayaran": "Belum Dibayar",
                        "Username": username
                    })
                    save_pending(pending)
                    print("Pesanan berhasil diajukan. Tunggu persetujuan admin.")
                    press_enter()
                    clear_screen()

                elif choice == "2":
                    my_queues = [item for item in data if isinstance(item, dict) and item.get("Username") == username]
                    if not my_queues:
                        print("Anda belum memiliki antrian.")
                        continue
                    my_queue_table = PrettyTable()
                    my_queue_table.field_names = ["No Antrian", "Nama", "No HP", "Alamat", "Keluhan", "Status", "Biaya", "Pembayaran", "Waktu"]
                    for item in my_queues:
                        my_queue_table.add_row([
                            item.get("Nomor Antrian", "N/A"),
                            item.get("Nama", "N/A"),
                            item.get("No HP", "N/A"),
                            item.get("Alamat", "N/A"),
                            item.get("Keluhan", "N/A"),
                            item.get("Status", "N/A"),
                            f"Rp.{item.get('Biaya', 0):,.0f}",
                            item.get("Status Pembayaran", "N/A"),
                            item.get("Waktu Daftar", "N/A")
                        ])
                    print(my_queue_table)
                    press_enter()
                    clear_screen()

                elif choice == "3":
                    customers = read_customers()
                    customer = next((c for c in customers if isinstance(c, dict) and c.get("username") == username), None)
                    if not customer:
                        print("Akun tidak ditemukan.")
                        continue
                    unpaid_services = [item for item in data if isinstance(item, dict) and item.get("Username") == username and item.get("Status") == "Selesai" and item.get("Status Pembayaran") == "Belum Dibayar"]
                    if not unpaid_services:
                        print("Tidak ada layanan yang perlu dibayar.")
                        continue
                    payment_table = PrettyTable()
                    payment_table.field_names = ["No Antrian", "Keluhan", "Biaya"]
                    for item in unpaid_services:
                        payment_table.add_row([item.get("Nomor Antrian", "N/A"), item.get("Keluhan", "N/A"), f"Rp.{item.get('Biaya', 0):,.0f}"])
                    print(payment_table)
                    try:
                        queue_num = int(input("Nomor Antrian yang dibayar: "))
                    except ValueError:
                        print("Input harus angka")
                        continue
                    service = next((item for item in unpaid_services if item.get("Nomor Antrian") == queue_num), None)
                    if not service:
                        print("Antrian tidak ditemukan.")
                        continue
                    pin_input = pwinput.pwinput("Masukkan PIN: ")
                    if pin_input != customer.get("pin", ""):
                        print("PIN salah.")
                        continue
                    cost = service.get("Biaya", 0)
                    if customer["saldo"] < cost:
                        print(f"Saldo tidak cukup. Saldo: Rp.{customer['saldo']:,.0f}, Biaya: Rp.{cost:,.0f}")
                        continue
                    customer["saldo"] -= cost
                    service["Status Pembayaran"] = "Terbayar"
                    global_balance = read_saldo()
                    global_balance["saldo"] += cost
                    save_saldo(global_balance)
                    save_customers(customers)
                    save_antrian(data)
                    create_receipt(customer, service, cost, time.strftime("%Y-%m-%d %H:%M:%S"))
                    print(f"Pembayaran berhasil. Saldo Anda: Rp.{customer['saldo']:,.0f}")

                elif choice == "4":
                    customers = read_customers()
                    customer = next((c for c in customers if isinstance(c, dict) and c.get("username") == username), None)
                    if customer:
                        print(f"Saldo Anda: Rp.{customer['saldo']:,.0f}")
                    else:
                        print("Akun tidak ditemukan.")
                    press_enter()
                    clear_screen()

                elif choice == "5":
                    customers = read_customers()
                    customer = next((c for c in customers if isinstance(c, dict) and c.get("username") == username), None)
                    if not customer:
                        print("Akun tidak ditemukan.")
                        continue
                    try:
                        amount = float(input("Jumlah top up: "))
                        if amount <= 0:
                            print("Jumlah harus lebih dari 0.")
                            continue
                    except ValueError:
                        print("Jumlah harus berupa angka.")
                        continue
                    pin_input = pwinput.pwinput("Masukkan PIN: ")
                    if pin_input != customer.get("pin", ""):
                        print("PIN salah.")
                        continue
                    customer["saldo"] += amount
                    save_customers(customers)
                    print(f"Top up berhasil! Saldo Anda: Rp.{customer['saldo']:,.0f}")

                elif choice == "6":
                    break
                else:
                    print("Pilihan tidak valid")
    except KeyboardInterrupt:
        print("\n\nKembali ke menu utama")
        return

# ==============================================================================
#                               MAIN MENU
# ==============================================================================

def main_menu():
    print("""
+===============================================================================+
|                 Selamat Datang di Layanan IT Support Yeheskiel                |
+===============================================================================+
|                 Solusi Terpercaya untuk Masalah Teknologi Anda                |
+===============================================================================+
""")
    try:
        while True:
            main_table = PrettyTable()
            main_table.title = "MENU UTAMA"
            main_table.field_names = ["No", "Menu"]
            main_table.add_row(["1", "Login"])
            main_table.add_row(["2", "Sign up"])
            main_table.add_row(["3", "Keluar"])
            print(main_table)
            choice = input("Pilih [1-3]: ").strip()
            clear_screen()
            if choice == "1":
                result = login()
                if result:
                    main_app(*result)
            elif choice == "2":
                signup()
            elif choice == "3":
                print("Terima kasih telah menggunakan layanan kami!")
                break
            else:
                print("Pilihan tidak valid.")
    except KeyboardInterrupt:
        print("\n\nProgram dihentikan oleh pengguna. Sampai jumpa!")
    except Exception as e:
        print(f"\nError tak terduga: {e}")
        print("Program dihentikan.")

if __name__ == "__main__":
    main_menu()
    