import pyodbc #sử dụng SQL Server
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
from datetime import date
import datetime
from tkcalendar import DateEntry
import pandas as pd

# ====== Hàm kết nối cơ sở dữ liệu SQL Server ======
def connect_db():
    try:
        con = pyodbc.connect(r'DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-F0T7LKA\SQLEXPRESS;DATABASE=QUANLYNHANSU;Trusted_Connection=yes;')
        return con
    
    except Exception as e:
        messagebox.showerror("Lỗi Kết Nối CSDL", f"Không thể kết nối đến SQL Server: {e}")
        return None

tai_khoan_hien_tai = ""
# ====== Hàm canh giữa cửa sổ ====== 
def center_window(win, w, h): 
    ws = win.winfo_screenwidth() 
    hs = win.winfo_screenheight() 
    x = (ws // 2) - (w // 2) 
    y = (hs // 2) - (h // 2) 
    win.geometry(f'{w}x{h}+{x}+{y}') 


#======= Xóa cửa sổ ======
def Clean_Window():
    for widget in root.winfo_children():
        widget.destroy()

root = tk.Tk()
root.title('HỆ THỐNG QUẢN LÝ NHÂN SỰ')
center_window(root,1100,700)
root.resizable(width=False, height=False)

FrameLogin = ttk.Frame(root)
topicLabel = tk.Label(FrameLogin,text = 'QUẢN LÍ NHÂN SỰ',font = ('Times New Roman',20,'bold'),bg = 'white')
topicLabel.grid(row=0,column=0,columnspan=2)
tk.Label(FrameLogin,font = (15)).grid(row=1,column=0)

root.resizable(width=True,height = True)
root.minsize(height = 563,width = 1000)

tk.Label(FrameLogin,text = 'Tên tài khoản:',font = ('Times New Roman',15),bg='white').grid(row=2,column=0)
tk.Label(FrameLogin,font=(15)).grid(row=3,column=0)
tk.Label(FrameLogin,text = 'Mật khẩu:',font = ('Times New Roman',15),bg='white').grid(row=4,column=0)

txtUser = tk.Entry(FrameLogin,width = 20,font = (15))
txtUser.grid(row=2,column=1)
txtUser.focus()


txtPass = tk.Entry(FrameLogin,width = 20,font=(15),show = '*')
txtPass.grid(row=4,column=1)

FrameLogin.place(x=310,y=210)

def show_password():
    if chk_Display.get():
        txtPass.config(show = '')
    else:
        txtPass.config(show = '*')

def Login():
        global tai_khoan_hien_tai
        user = txtUser.get()
        password = txtPass.get()

        con = connect_db()
        cur = con.cursor()
        #đếm số lượng tài khoản với mã nhân viên và mật khẩu trùng khớp
        cur.execute("SELECT COUNT(*) FROM TAIKHOAN WHERE TENTAIKHOAN = ? AND PASS = ?",(user,password))
        result = cur.fetchone()[0]
        if result: #nếu có 1 tài khoản trừng khớp thì cho phép đăng nhập
            messagebox.showinfo('Thông báo','Đăng nhập thành công!')
            tai_khoan_hien_tai = txtUser.get()
            Clean_Window()
            main()
            return
        #không đăng nhập được, thực hiện kiểm tra xem mã nhân viên được nhập có phải làm ở phodng nhân sự hoặc là giám đốc hay không
        # (giới hạn nhân viên được phép truy cập vào hệ thống)
        #điều kiện này đồng thời lồng ghép với điều kiện mã nhân viên có tồn tại hay không (vì không có thì sẽ được thông báo là không đúng đối tượng)
        cur.execute("SELECT COUNT(*) FROM NHANVIEN WHERE MANV = ? AND (PHONGBAN = N'Nhân sự' OR CHUCVU = N'Giám đốc')",(user))
        if cur.fetchone()[0]>0:
            #nếu đúng đối tượng trên, tiếp tục kiểm tra xem mã nhân viên đã tồn tại hay chưa (chưa xét tới đúng mật khẩu hay không)
            cur.execute("SELECT COUNT(*) FROM NHANVIEN WHERE MANV = ? AND (PHONGBAN = N'Nhân sự' OR CHUCVU = N'Giám đốc')",(user))
            if cur.fetchone()[0]>0:
                messagebox.showwarning("thông báo","Tài khoản không tồn tại")
                tb = messagebox.askyesno("thông báo","bạn muốn tạo tài khoản không?")
                if tb>0:
                    tao() #không có tên tài khoản tồn tại đúng với mã nhân viên thì thông báo hỏi tạo tài khoản
            else:
                #mã nhân viên đã tồn tại (select được !=0 dòng tác động thì báo mật khẩu không trùng khớp 
                # vì nếu trùng khớp và đúng mật khẩu thì đã thực hiện được dòng if trên cùng)
                messagebox.showerror('Lỗi','Mã nhân viên hoặc mật khẩu không đúng!')
        else:
            #mã nhân viên không phù hợp với điều kiện thì thông báo nhân viên không thuộc đối tượng truy cập 
            # (không cần kiểm tra xem tài khoản tồn tại hay chưa để tạo hay thông báo sai mật khẩu)
            messagebox.showwarning("thông báo","bạn không thuộc đối tượng có thể truy cập hệ thống")
        
def Thoat():
        exit = messagebox.askyesno('Thoát','Bạn có chắc chắn muốn thoát không?')
        if exit>0:
            root.destroy()
            return

def tao():
    
    root.withdraw()
    mk = tk.Toplevel()
    mk.title('TẠO TÀI KHOẢN')
    center_window(mk,1000,700)
    mk.resizable(width=False, height=False)
    
    def themtk():
        username = username_entrytk.get()
        matkhau = pass_entrytk.get()
        xnmk = passxn_entrytk.get()

        #điều kiện mật khẩu phải đủ dài (4-10) kí tự
        if len(matkhau)>10 or len(matkhau)<4:
            messagebox.showwarning("thông báo","vui lòng nhập mật khẩu từ 4 đến 10 kí tự")
            return
        #mật khẩu xác nhận trùng khớp với mật khẩu muốn đặt
        if matkhau == xnmk:
            con = connect_db() 
            cur = con.cursor()
            try: 
                #yêu cầu nhập đầy đủ thông tin cần thiết
                if username == "" or matkhau == "":
                    messagebox.showwarning("thiếu dữ liệu","vui lòng nhập đầy đủ thông tin")
                    return
                #kiểm tra mã nhân viên cần tạo có đúng đối tượng hay không 
                # (trừ trường hợp ở cửa sổ login nhập mã nhân viên nhầm lẫn giữa 2 loại thao tác là đăng nhập sai mât khẩu và tạo tài khoản mới)
                #điều kiện này đồng thời lồng ghép với điều kiện mã nhân viên có tồn tại hay không 
                # (vì không có thì sẽ được thông báo là không đúng đối tượng)
                cur.execute("""SELECT COUNT(*) FROM NHANVIEN WHERE (MANV = ? AND CHUCVU = N'Giám đốc') OR (MANV=? AND PHONGBAN = N'Nhân sự')""", (username,username))
                if cur.fetchone()[0] == 0 :
                    messagebox.showwarning("Lỗi","Chỉ Giám đốc hoặc nhân viên thuộc phòng nhân sự mới có thể tạo tài khoản")
                    return
                #đảm bảo tên tài khoản(ứng với mã nhân viên) không bị tạo thêm lần thứ 2
                cur.execute("SELECT COUNT(*) FROM TAIKHOAN WHERE TENTAIKHOAN = ?",(username,))
                if cur.fetchone()[0]!= 0:
                    messagebox.showwarning("Lỗi","Tài khoản đã tồn tại, vui lòng chọn tên tài khoản khác")
                    return
                #đúng đối tượng và chưa có tài khoản thì cho phép tạo tài khoản thành công
                cur.execute("INSERT INTO TAIKHOAN (TENTAIKHOAN,PASS) VALUES (?,?)", (username,matkhau))
                con.commit()
                messagebox.showinfo("thông báo","Đã tạo tài khoản thành công") 
                root.deiconify()
                mk.destroy()
            except Exception as e: 
                messagebox.showerror("Lỗi", str(e)) 
            con.close()
        else:
            #mật khẩu muốn đặt và mật khẩu xác nhận không trùng khớp được thông báo để nhập lại
            messagebox.showwarning("thông báo","vui lòng nhập đúng mật khẩu xác nhận")
            return

    def huytk():
      username_entrytk.delete(0,tk.END)
      pass_entrytk.delete(0,tk.END)
      passxn_entrytk.delete(0,tk.END)
      username_entrytk.focus()

    def thoattk():
      exit = messagebox.askyesno('Thoát','Bạn có chắc chắn muốn thoát không?')
      if exit>0:
        root.deiconify()
        mk.destroy()
        return

    FrameTK = ttk.Frame(mk)
    ttk.Label(FrameTK,text = 'TẠO TÀI KHOẢN',font = ('Times New Roman',20,'bold')).grid(row=0,column=0,columnspan=2)
    ttk.Label(FrameTK,font = (10)).grid(row=1,column=0)
    ttk.Label(FrameTK,text = 'Tên tài khoản: ',font = ('Times New Roman',15)).grid(row=2,column=0)
    username_entrytk = ttk.Entry(FrameTK,font = (15),width=20)
    username_entrytk.grid(row=2,column=1)
    ttk.Label(FrameTK,font = (10)).grid(row=3,column=0)
    ttk.Label(FrameTK,text = 'Mật khẩu: ',font = ('Times New Roman',15)).grid(row=4,column=0)
    pass_entrytk = ttk.Entry(FrameTK,font = (15),width=20)
    pass_entrytk.grid(row=4,column=1)
    ttk.Label(FrameTK,font = (10)).grid(row=5,column=0)
    ttk.Label(FrameTK,text = 'Xác nhận mật khẩu: ',font = ('Times New Roman',15)).grid(row=6,column=0)
    passxn_entrytk = ttk.Entry(FrameTK,font = (15),width=20)
    passxn_entrytk.grid(row=6,column=1)
    ttk.Label(FrameTK,font = (10)).grid(row=7,column=0)
    FrameButtonTK = ttk.Frame(FrameTK)
    btnTao = tk.Button(FrameButtonTK,text = 'Tạo',font = ('Times New Roman',15),cursor = 'hand2',command = themtk)
    btnTao.pack(side=tk.LEFT)
    ttk.Label(FrameButtonTK,width=15).pack(side=tk.LEFT)
    btnHuy = tk.Button(FrameButtonTK,text = 'Hủy',font = ('Times New Roman',15),cursor = 'hand2',command = huytk)
    btnHuy.pack(side=tk.LEFT)
    ttk.Label(FrameButtonTK,width=15).pack(side=tk.LEFT)
    btnThoat = tk.Button(FrameButtonTK,text = 'Thoát',font = ('Times New Roman',15),cursor = 'hand2',command = thoattk)
    btnThoat.pack(side=tk.LEFT)
    FrameButtonTK.grid(row=8,column=0,columnspan=2)
    FrameTK.place(x=285,y=210)


tk.Label(FrameLogin,font=(15)).grid(row=5,column=0)
chk_Display = tk.BooleanVar()
chk = tk.Checkbutton(FrameLogin,text = 'Hiển thị mật khẩu',bg='white',variable=chk_Display,command=show_password)
chk.grid(row=6,column=1)
            
tk.Label(FrameLogin,font=(15)).grid(row=7,column=0)

FrameButtonLogin = ttk.Frame(FrameLogin)
btnLogin = tk.Button(FrameButtonLogin,text = 'Đăng nhập',font = ('Times New Roman',15),cursor = 'hand2',command=Login)
btnLogin.pack(side=tk.LEFT)

ttk.Label(FrameButtonLogin,width = 10).pack(side = tk.LEFT)

btnTaoTK = tk.Button(FrameButtonLogin,text = 'Tạo tài khoản',font = ('Times New Roman',15),cursor = 'hand2',command=tao)
btnTaoTK.pack(side=tk.LEFT)
ttk.Label(FrameButtonLogin,width = 10).pack(side = tk.LEFT)
btnExit = tk.Button(FrameButtonLogin,text = 'Thoát',font = ('Times New Roman',15),cursor = 'hand2',command=Thoat)
btnExit.pack(side=tk.LEFT)
FrameButtonLogin.grid(row=8,column=0,columnspan=2)

def main():
    def thoat_ht():
        tb = messagebox.askyesno("Xác nhận","bạn muốn thoát khỏi chương trình?")
        if tb>0:
            root.destroy()
            return
    cmb_font = ('Times New Roman',15)
    #================================================================================================Tab Nhân Viên================
    tab_control = ttk.Notebook(root)
    tabNhanVien = ttk.Frame(tab_control)
    tab_control.add(tabNhanVien,text = "DANH SÁCH NHÂN VIÊN")
    tab_control.pack(expand=1,fill='both')
    FrametabNhanvien = ttk.Frame(tabNhanVien)
    ttk.Label(FrametabNhanvien,text ="QUẢN LÝ NHÂN VIÊN",font = ("Times New Roman",20,'bold'),justify = tk.CENTER).grid(row=0,column=0,columnspan=7)

    ttk.Label(FrametabNhanvien,font=(15)).grid(row=1,column=0)
    
    lblFrame1 = ttk.Frame(FrametabNhanvien)
    ttk.Label(lblFrame1,text = 'Mã nhân viên:',font = ('Times New Roman',15),justify = tk.LEFT).pack(side=tk.TOP)
    ttk.Label(lblFrame1,font = (10)).pack(side=tk.TOP)
    ttk.Label(lblFrame1,text = 'Họ tên:',font = ('Times New Roman',15),justify = tk.LEFT).pack(side=tk.TOP)
    ttk.Label(lblFrame1,font = (10)).pack(side=tk.TOP)
    ttk.Label(lblFrame1,text = 'Phòng ban:',font = ("Times New Roman",15),justify = tk.LEFT).pack(side=tk.TOP)
    ttk.Label(lblFrame1,font = (10)).pack(side=tk.TOP)
    ttk.Label(lblFrame1,text = 'Chức vụ:',font = ('Times New Roman',15),justify = tk.LEFT).pack(side=tk.TOP)
    ttk.Label(lblFrame1,font = (10)).pack(side=tk.TOP)
    ttk.Label(lblFrame1,text = 'Thâm niên: ',font = ('Times New Roman',15),justify = tk.LEFT).pack(side=tk.TOP)
    ttk.Label(lblFrame1,font = (10)).pack(side=tk.TOP)
    lblFrame1.grid(row=2,column=0)

    ttk.Label(FrametabNhanvien,width=10).grid(row=2,column=1)

    stringMaNV = tk.StringVar()
    stringHoTenNV = tk.StringVar()
    intThamNien = tk.IntVar()

    Frame1 = ttk.Frame(FrametabNhanvien)
    manv_entrynv = ttk.Entry(Frame1,font = (15),width=20,textvariable = stringMaNV)
    manv_entrynv.pack(side=tk.TOP)
    ttk.Label(Frame1,font = (10)).pack(side=tk.TOP)
    tennv_entrynv=ttk.Entry(Frame1,font = (15),width=20,textvariable = stringHoTenNV)
    tennv_entrynv.pack(side=tk.TOP)
    ttk.Label(Frame1,font = (10)).pack(side=tk.TOP)

    cmbPhongBan = ttk.Combobox(Frame1,width = 20,font = cmb_font)
    cmbPhongBan['values']=('(Chọn phòng ban)','Giám đốc','Nhân sự','Tài chính','Kỹ thuật','Kinh doanh','Marketing','Hành chính')
    cmbPhongBan.current(0)
    cmbPhongBan.pack(side=tk.TOP)
    ttk.Label(Frame1,font = (10)).pack(side=tk.TOP)

    cmbChucVu = ttk.Combobox(Frame1,font = cmb_font)
    cmbChucVu['values']=('(Chọn chức vụ)','Giám đốc','Trưởng phòng','Quản lý','Nhân viên','Phó phòng','Thực tập sinh')
    cmbChucVu.current(0)
    cmbChucVu.pack(side=tk.TOP)
    ttk.Label(Frame1,font = (10)).pack(side=tk.TOP)

    thamnien_entrynv=ttk.Entry(Frame1,font = (15),width=20,textvariable = intThamNien)
    thamnien_entrynv.pack(side=tk.TOP)
    ttk.Label(Frame1,font = (10)).pack(side=tk.TOP)

    Frame1.grid(row=2,column=2)

    ttk.Label(FrametabNhanvien,width=10).grid(row=2,column=3)

    
    lblFrame2 = ttk.Frame(FrametabNhanvien)
    ttk.Label(lblFrame2,text = 'CCCD:',font = ('Times New Roman',15),justify = tk.LEFT).pack(side=tk.TOP)
    ttk.Label(lblFrame2,font = (10)).pack(side=tk.TOP)
    ttk.Label(lblFrame2,text = 'Email:',font = ('Times New Roman',15),justify = tk.LEFT).pack(side=tk.TOP)
    ttk.Label(lblFrame2,font = (10)).pack(side=tk.TOP)
    ttk.Label(lblFrame2,text = 'Ngày sinh:',font = ('Times New Roman',15),justify = tk.LEFT).pack(side=tk.TOP)
    ttk.Label(lblFrame2,font = (10)).pack(side=tk.TOP)
    ttk.Label(lblFrame2,text = 'Điện thoại: ',font = ('Times New Roman',15),justify = tk.LEFT).pack(side = tk.TOP)
    ttk.Label(lblFrame2,font = (10)).pack(side=tk.TOP)
    ttk.Label(lblFrame2,text = 'Giới tính: ',font = ('Times New Roman',15),justify = tk.LEFT).pack(side = tk.TOP)
    ttk.Label(lblFrame2,font = (10)).pack(side = tk.TOP)
    lblFrame2.grid(row = 2,column=4)

    ttk.Label(FrametabNhanvien,width=5).grid(row=2,column=5)
    
    Frame2 = ttk.Frame(FrametabNhanvien)

    stringCCCD = tk.StringVar()
    stringEmail = tk.StringVar()
    stringDienThoai = tk.StringVar()
    stringGioiTinh = tk.StringVar(value='Nam')

    cccd_entrynv=ttk.Entry(Frame2,font = (15),width=20,textvariable = stringCCCD)
    cccd_entrynv.pack(side=tk.TOP)
    ttk.Label(Frame2,font = (10)).pack(side=tk.TOP)

    mail_entrynv=ttk.Entry(Frame2,font = (15),width=25,textvariable = stringEmail)
    mail_entrynv.pack(side=tk.TOP)
    ttk.Label(Frame2,font = (10)).pack(side=tk.TOP)

    ngaysinh_dateentrynv=DateEntry(Frame2,font = (15),width=20, background="darkblue", foreground="white", date_pattern="yyyy-mm-dd")
    ngaysinh_dateentrynv.pack(side=tk.TOP)
    ttk.Label(Frame2,font = (10)).pack(side = tk.TOP)

    dienthoai_entrynv = ttk.Entry(Frame2,font = (15),width=20,textvariable = stringDienThoai)
    dienthoai_entrynv.pack(side=tk.TOP)
    ttk.Label(Frame2,font = (10)).pack(side=tk.TOP)

    FrameGT = ttk.Frame(Frame2)
    ttk.Radiobutton(FrameGT, text = 'Nam',variable = stringGioiTinh,value = 'Nam').pack(side=tk.LEFT)
    ttk.Label(FrameGT,width=10).pack(side=tk.LEFT)
    ttk.Radiobutton(FrameGT,text = 'Nữ',variable = stringGioiTinh,value = 'Nữ').pack(side=tk.LEFT)
    FrameGT.pack(side=tk.TOP)
    ttk.Label(Frame2,font = (10)).pack(side = tk.TOP)
    Frame2.grid(row=2,column=6)

    def load_data_nv():
        for i in tree.get_children():
            tree.delete(i)
        con = connect_db()
        if con is None: return
        cur = con.cursor()
        try:
            cur.execute('SELECT * FROM NHANVIEN')
            for row in cur:
                data_list = list(row)
                for i, item in enumerate(data_list):
                    if isinstance(item, datetime.date):
                        data_list[i] = item.strftime('%Y-%m-%d')
                tree.insert('', tk.END, values=data_list)
        except Exception as e:
            messagebox.showerror("Lỗi Truy vấn", f"Lỗi khi thực thi truy vấn: {e}")
        con.close()
        clear_input()
    
    def clear_input():
        manv_entrynv.delete(0,tk.END)
        tennv_entrynv.delete(0,tk.END)
        cmbPhongBan.current(0)
        cmbChucVu.current(0)
        thamnien_entrynv.delete(0,tk.END)
        cccd_entrynv.delete(0,tk.END)
        mail_entrynv.delete(0,tk.END)
        ngaysinh_dateentrynv.set_date(date.today()) 
        dienthoai_entrynv.delete(0,tk.END)
        stringGioiTinh.set('Nam')
        timnv_entrynv.delete(0,tk.END)

    def them_nv():
        manv = manv_entrynv.get()
        ten = tennv_entrynv.get()
        phongban = cmbPhongBan.get()
        chucvu = cmbChucVu.get()
        thamnien = thamnien_entrynv.get() 
        cccd = cccd_entrynv.get()
        mail = mail_entrynv.get()
        ngaysinh = ngaysinh_dateentrynv.get_date()
        dienthoai = dienthoai_entrynv.get()
        gioitinh = stringGioiTinh.get()

        #các item đảm bảo được nhập đủ thông tin trước khi tiến hành xử lý
        if not all([manv, ten, phongban, chucvu, cccd, mail, dienthoai, gioitinh,thamnien]):
            messagebox.showwarning("thiếu dữ liệu","vui lòng nhập đủ thông tin")
            return
        #khi thêm nhân viên mới thì nhân viên đó phải có thâm niên = 0 (sẽ được thay đổi đúng sau khi thêm hợp đồng)
        if int(thamnien) !=0:
            messagebox.showwarning("thông báo","không được nhập thâm niên khác 0 khi thêm nhân viên mới")
        #mã nhân viên đúng định dạng 'NV[0-9][0-9][0-9]'
        if len(manv)!=5 or manv[0:2]!='NV':
            messagebox.showwarning("thông báo","vui lòng mã nhân viên 5 kí tự bắt đầu bằng 'NV'")
            return
        #kiểm tra 3 kí tự cuối của mã nhân viên là số
        try:
            result = float(manv[2:])
        except ValueError:
            messagebox.showwarning("Lỗi", "Mã nhân viên không phù hợp, vui lòng kiểm tra lại")
            return
        #nếu tên nhân viên quá dài thì được yêu cầu nhập lại
        if len(ten)>100:
            messagebox.showwarning("thông báo","vui lòng nhập tên ngắn gọn dưới 100 kí tự")
            return
        #email không quá 100 kí tự
        if len(mail)>100:
            messagebox.showwarning("thông báo","vui lòng nhập email không quá 100 kí tự")
            return
        
        #điện thoại phải là 10 số
        if len(dienthoai)!=10:
            messagebox.showwarning("thông báo","số điện thoại đủ 10 số")
        try:
            result = float(dienthoai)
        except ValueError:
            messagebox.showwarning("Lỗi", "Điện thoại phải là số.")
            return
        
        #phòng ban và chức vụ được cố định (không được chọn hay nhập ngoài thì nó đã không tồn tại trong công ty)
        if phongban not in ('Giám đốc','Nhân sự','Tài chính','Kỹ thuật','Kinh doanh','Marketing','Hành chính'):
            messagebox.showwarning("thông báo","vui lòng chọn phòng ban phù hợp")
            return
        if chucvu not in ('Giám đốc','Trưởng phòng','Quản lý','Nhân viên','Phó phòng','Thực tập sinh'):
            messagebox.showwarning("thông báo","vui lògn chọn chức vụ phù hợp")
            return
        
        #giới hạn độ tuổi nhân viên (chỉ xét năm sinh)
        today = date.today()
        if (today.year - ngaysinh.year < 18):
            messagebox.showwarning("thông báo","vui lòng chọn ngày sinh phù hợp (nhân viên phải đủ 18 tuổi)")
            return
        #nếu còn các giá trị sau đây sẽ được thông báo chọn giá trị hợp lệ
        if phongban == '(Chọn phòng ban)' or chucvu == '(Chọn chức vụ)':
            messagebox.showwarning("thông báo","vui lòng chọn phòng ban và chức vụ phù hợp")
            return
        #nếu nhập thông tin cho giám đốc thì giám đốc chỉ làm việc cho phòng giám đốc
        #không đặt điều kiện ngược lại vì phòng ban giám đốc thì có thể có nhiều chức vụ khác cùng làm trong phòng giám đốc
        if chucvu == 'Giám đốc' and phongban != 'Giám đốc':
            messagebox.showwarning("thông báo","Giám đốc chỉ thuộc phòng Giám đốc")
            return

        con = connect_db()
        if con is None: return
        cur = con.cursor()
        try:
            #kiểm tra mã nhân viên, cccd, điện thoại và email đã tồn tại chưa vì những dữ liệu trên là riêng biệt giữa các nhân viên (UNIQUE)
            cur.execute("SELECT COUNT(*) FROM NHANVIEN WHERE MANV=?", (manv,))
            if cur.fetchone()[0] > 0:
                messagebox.showwarning("Lỗi","Mã nhân viên đã tồn tại, vui lòng chọn mã khác")
                return
            cur.execute("SELECT COUNT(*) FROM NHANVIEN WHERE CCCD=?", (cccd,))
            if cur.fetchone()[0] > 0:
                messagebox.showwarning("Lỗi","CCCD đã tồn tại, vui lòng kiểm tra lại")
                return
            cur.execute("SELECT COUNT(*) FROM NHANVIEN WHERE DIENTHOAI=?", (dienthoai,))
            if cur.fetchone()[0] > 0:
                messagebox.showwarning("Lỗi","Số điện thoại đã tồn tại, vui lòng kiểm tra lại")
                return
            cur.execute("SELECT COUNT(*) FROM NHANVIEN WHERE EMAIL =?",(mail,))
            if cur.fetchone()[0] >0:
                messagebox.showwarning("Lỗi","Email đã tồn tại, vui lòng kiểm tra lại")
            #các điều kiện trên hợp lệ thì cho phép thêm thông tin nhân viên mới vào hệ thống
            cur.execute("INSERT INTO NHANVIEN VALUES (?,?,?,?,?,?,?,?,?,?)", \
                        (manv, ten, cccd, dienthoai, gioitinh, mail, ngaysinh, phongban, chucvu, thamnien))
            con.commit()
            messagebox.showinfo("Thành công", "Đã thêm nhân viên thành công.")
            con.close()
            #load lại toàn bộ danh sách nhân viên để hiển thị thêm thông tin nhân viên vói vào hệ thống
            load_data_nv()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
        

    def xoa_nv():
        global tai_khoan_hien_tai
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Chưa chọn", "Hãy chọn nhân viên để xóa")
            return
        manv = tree.item(selected)["values"][0]
        #với tài khoản đang được đăng nhập thì nhân viên đó không được xóa thông tin của mình (còn dữ liệu tài khoản)
        #nêu muốn xóa thì bắt buộc không còn tồn tại thông tin: hợp đồng, lương, chi tiết lương và tài khoản (nếu có)
        # vì vậy điều này phải được thực hiện bởi 1 nhân viên khác
        #vì ngay ban đầu đã giới hạn nhân viên có phận sự truy cập vào hệ thống nên tất cả các thao tác trong hệ thống được quản trị an toàn hơn 
        # (không thực hiện quá bừa bãi)
        if manv == tai_khoan_hien_tai:
            messagebox.showwarning("Không thể xóa", "Bạn đang đăng nhập bằng tài khoản này, không thể xóa.")
            return

        con = connect_db()
        if con is None: return
        cur = con.cursor()
        
        try:
            #không thể xóa thông tin giám đốc trực tiếp, nếu giám đốc đó từ chức (nếu có) 
            # thông tin cần xóa có thể thay đổi chức vụ khác rồi có thể thực hiện xóa
            cur.execute("SELECT COUNT(*) FROM NHANVIEN WHERE MANV=? AND CHUCVU = N'Giám đốc'", (manv,))
            if cur.fetchone()[0] != 0:
                messagebox.showwarning("Không thể xóa", "Không thể xóa Giám đốc khỏi hệ thống.")
                return
            #nếu thông tin nhân viên muốn xóa còn được lưu trong hệ thống để quản lý thì không cho phép xóa
            cur.execute("SELECT COUNT(*) FROM HOPDONG WHERE MANV=?", (manv,))
            if cur.fetchone()[0] > 0:
                messagebox.showwarning("Không thể xóa", "Nhân viên này có lịch sử hợp đồng, không thể xóa.")
                return
            cur.execute("SELECT COUNT(*) FROM LUONG WHERE MANV=?", (manv,))
            if cur.fetchone()[0] > 0:
                messagebox.showwarning("Không thể xóa", "Nhân viên này có dữ liệu lương, không thể xóa.")
                return
            cur.execute("SELECT COUNT(*) FROM CONG_NGAY WHERE MANV=?", (manv,))
            if cur.fetchone()[0] > 0:
                messagebox.showwarning("Không thể xóa", "Nhân viên này có dữ liệu công ngày, không thể xóa.")
                return
            cur.execute("SELECT COUNT(*) FROM CHITIETLUONG WHERE MANV=?", (manv,))
            if cur.fetchone()[0] > 0:
                messagebox.showwarning("Không thể xóa", "Nhân viên này có dữ liệu chi tiết lương, không thể xóa.")
                return
            #phù hợp các yêu cầu trên, khi xóa thông tin nhân viên thì xóa tài khoản đăng nhập hệ thống của họ (nếu có)
            #tài khoản tồn tại không nằm ở các điều kiện trên vì tài khoản được lưu chỉ dành cho những nhân viên tiếp tục làm việc ở công ty 
            # và khi nhân viên đó xóa thông tin của họ thì đồng nghĩa họ chỉ không tiếp tục làm và chỉ cần xóa trực tiếp tài khoản của họ
            cur.execute("DELETE FROM TAIKHOAN WHERE TENTAIKHOAN=?", (manv,))
            cur.execute("DELETE FROM NHANVIEN WHERE MANV = ?", (manv,))
            con.commit()
            messagebox.showinfo("Xóa thành công", "Đã xóa nhân viên thành công.")
            
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
        con.close()
        load_data_nv()

    def sua_nv():
        selected = tree.selection() 
        if not selected: 
            messagebox.showwarning("Chưa chọn", "Hãy chọn nhân viên để sửa") 
            return 
        luu_nv()

    def luu_nv():
        global tai_khoan_hien_tai
        manv = manv_entrynv.get()
        ten = tennv_entrynv.get()
        phongban = cmbPhongBan.get()
        chucvu = cmbChucVu.get()
        cccd = cccd_entrynv.get()
        mail = mail_entrynv.get()
        ngaysinh = ngaysinh_dateentrynv.get_date()
        dienthoai = dienthoai_entrynv.get()
        gioitinh = stringGioiTinh.get()
        

        if not all([manv_entrynv, ten, phongban, chucvu, cccd, mail, dienthoai, gioitinh, thamnien_entrynv]):
            messagebox.showwarning("thiếu dữ liệu","vui lòng nhập đủ thông tin")
            return
            
        if len(manv)!=5 or manv[0:2]!='NV':
            messagebox.showwarning("thông báo","vui lòng mã nhân viên 5 kí tự bắt đầu bằng 'NV'")
            return
        if len(ten)>100:
            messagebox.showwarning("thông báo","vui lòng nhập tên ngắn gọn dưới 100 kí tự")
            return
        if phongban not in ('Giám đốc','Nhân sự','Tài chính','Kỹ thuật','Kinh doanh','Marketing','Hành chính'):
            messagebox.showwarning("thông báo","vui lòng chọn phòng ban phù hợp")
            return
        if chucvu not in ('Giám đốc','Trưởng phòng','Quản lý','Nhân viên','Phó phòng','Thực tập sinh'):
            messagebox.showwarning("thông báo","vui lògn chọn chức vụ phù hợp")
            return
        today = date.today()
        if (today.year - ngaysinh.year < 18):
            messagebox.showwarning("thông báo","vui lòng chọn ngày sinh phù hợp (nhân viên phải đủ 18 tuổi)")
            return
            
        if phongban == '(Chọn phòng ban)' or chucvu == '(Chọn chức vụ)':
            messagebox.showwarning("thông báo","vui lòng chọn phòng ban và chức vụ phù hợp")
            return
        
        if chucvu == 'Giám đốc' and phongban != 'Giám đốc':
            messagebox.showwarning("thông báo","Giám đốc chỉ thuộc phòng Giám đốc")
            return
        #nếu đổi thông tin đang đăng nhập thì không đổi phòng ban hoặc chức vụ ngoài giới hạn đăng nhập
        if manv == tai_khoan_hien_tai and (phongban != 'Nhân sự' or chucvu != 'Giám đốc'):
            messagebox.showwarning("thông báo","không thể thay đổi phòng ban nhân sự hoặc chức vụ giám đốc của bạn" \
            " trong khi tài khoản của bạn đang đăng nhập")
            return
        
        selected = tree.selection()
        #lấy mã nhân viên được chọn từ cây đối chiếu với mã nhân viên được hiển thị trên entry
        #nếu nhập mới để sửa thì thông báo không được sửa mã nhân viên và lấy mã nhân viên từ danh sách đã được lưu
        old_manv = tree.item(selected)["values"][0] 
            
        if manv != old_manv:
            messagebox.showwarning("thông báo","không thể thay đổi mã nhân viên")
            manv_entrynv.delete(0,tk.END)
            manv_entrynv.insert(0,old_manv)
            return
        
        con = connect_db()
        if con is None: return
        cur = con.cursor()
        
        try:
            #kiểm tra các giá trị cccd, dienthoai và email muốn đổi cho nhân viên này không trùng với nhân viên khác
            # kể cả không thay đổi giá trị khác
            cur.execute("SELECT COUNT(*) FROM NHANVIEN WHERE CCCD=? AND MANV != ?", (cccd,old_manv))
            if cur.fetchone()[0] > 0:
                messagebox.showwarning("Lỗi","CCCD đã tồn tại, vui lòng kiểm tra lại")
                return
            cur.execute("SELECT COUNT(*) FROM NHANVIEN WHERE DIENTHOAI=? AND MANV != ?", (dienthoai,old_manv))
            if cur.fetchone()[0] > 0:
                messagebox.showwarning("Lỗi","Số điện thoại đã tồn tại, vui lòng kiểm tra lại")
                return
            cur.execute("SELECT COUNT(*) FROM NHANVIEN WHERE EMAIL =? AND MANV != ?",(mail,old_manv))
            if cur.fetchone()[0] >0:
                messagebox.showwarning("Lỗi","Email đã tồn tại, vui lòng kiểm tra lại")
            cur.execute("""
                UPDATE NHANVIEN 
                SET HOTEN = ? , CCCD = ?, DIENTHOAI =?, GIOITINH = ?, EMAIL = ?, NGAYSINH = ?, PHONGBAN = ?, CHUCVU = ?
                WHERE MANV = ?
                """, 
                (ten, cccd, dienthoai, gioitinh, mail, ngaysinh, phongban, chucvu, old_manv)
            )
            con.commit()
            messagebox.showinfo("Thành công", "Đã sửa thông tin nhân viên thành công.")
            #nhân viên được chọn để sửa thông tin (trừ mã nhân viên), kiểm tra xem nhân viên này có đổi chức vụ hay phòng ban để xử lý tài khoản đăng
            #nhập hệ thống
            #đặt trường hợp đã có tài khoản nhưng nhân viên đó chuyển công tác sang công việc khác mà không có phận sự đăng nhập hệ thống
            cur.execute("SELECT COUNT(*) FROM NHANVIEN WHERE MANV = ? AND (PHONGBAN = N'Nhân sự' OR CHUCVU = N'Giám đốc')",(old_manv,))
            if cur.fetchone()[0] == 0:
                cur.execute("DELETE FROM TAIKHOAN WHERE TENTAIKHOAN = ?",(old_manv,))
            con.commit()  
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
        con.close()
        load_data_nv()

    def load_data_tim(string):
        for i in tree.get_children():
            tree.delete(i)
        con = connect_db()
        if con is None: return
        cur = con.cursor()
        try:
            cur.execute(string)
            for row in cur:
                data_list = list(row)
                for i, item in enumerate(data_list):
                    if isinstance(item, datetime.date):
                        data_list[i] = item.strftime('%Y-%m-%d')
                tree.insert('', tk.END, values=data_list)
        except Exception as e:
            messagebox.showerror("Lỗi Truy vấn", f"Lỗi khi thực thi truy vấn: {e}")
        con.close()
    
    def tim_nv():
        tim = cmbTimNV.get()
        entry = timnv_entrynv.get()
        if (tim == 'Mã nhân viên'):
            load_data_tim("SELECT * FROM NHANVIEN WHERE MANV = '"+entry+"'")
            
        elif (tim == 'Họ tên'):
            load_data_tim("SELECT * FROM NHANVIEN WHERE HOTEN = '"+entry+"'")

        elif (tim == 'CCCD'):
            load_data_tim("SELECT * FROM NHANVIEN WHERE CCCD = '"+entry+"'")

        elif (tim == 'Điện thoại'):
            load_data_tim("SELECT * FROM NHANVIEN WHERE DIENTHOAI = '"+entry+"'")

        elif (tim == 'Giới tính'):
            if entry not in ['Nam','Nữ']:
                messagebox.showwarning("thông báo","vui lòng nhập đúng giới tính (Nam hoặc Nữ)")
                return
            load_data_tim("SELECT * FROM NHANVIEN WHERE GIOITINH = '"+entry+"'")

        elif (tim == 'Email'):
            load_data_tim("SELECT * FROM NHANVIEN WHERE EMAIL = '"+entry+"'")

        elif (tim == 'Phòng ban'):
            if entry not in ['Giám đốc','Nhân sự','Tài chính','Kỹ thuật','Kinh doanh','Marketing','Hành chính']:
                messagebox.showwarning("thông báo","phòng ban không tồn tại, vui lòng tìm phòng ban khác")
                return
            load_data_tim("SELECT * FROM NHANVIEN WHERE PHONGBAN = N'"+entry+"'")

        elif (tim == 'Chức vụ'):
            if entry not in ['Giám đốc','Trưởng phòng','Quản lý','Nhân viên','Phó phòng','Thực tập sinh']:
                messagebox.showwarning("thông báo","chức vụ không tồn tại, vui lòng chọn chức vụ khác")
            load_data_tim("SELECT * FROM NHANVIEN WHERE CHUCVU = N'"+entry+"'")
        elif (tim == 'Thâm niên'):
            load_data_tim("SELECT * FROM NHANVIEN WHERE THAMNIEN='"+entry+"'")
        else:
            messagebox.showwarning("thông báo","vui lòng chọn đúng danh mục tìm kiếm")
            return      

    
    FrameButton = ttk.Frame(FrametabNhanvien)
    btnThemNV=tk.Button(FrameButton,text = 'Thêm',font = ('Times New Roman',15),cursor = 'hand2',command = them_nv)
    btnThemNV.pack(side=tk.LEFT)
    ttk.Label(FrameButton,width=5).pack(side=tk.LEFT)
    btnXoaNV=tk.Button(FrameButton,text = 'Xóa',font = ('Times New Roman',15),cursor = 'hand2',command = xoa_nv)
    btnXoaNV.pack(side=tk.LEFT)
    ttk.Label(FrameButton,width=5).pack(side=tk.LEFT)
    btnSuaNV=tk.Button(FrameButton,text = 'Sửa',font=('Times New Roman',15),cursor = 'hand2',command = sua_nv)
    btnSuaNV.pack(side=tk.LEFT)
    ttk.Label(FrameButton,width=5).pack(side=tk.LEFT)
    btnHuyNV=tk.Button(FrameButton,text = 'Hủy',font = ('Times New Roman',15),cursor = 'hand2',command = clear_input)
    btnHuyNV.pack(side=tk.LEFT)
    
    ttk.Label(FrameButton,width=5).pack(side=tk.LEFT)
    cmbTimNV = ttk.Combobox(FrameButton,width=20,font=cmb_font)
    cmbTimNV['values'] = ('Mã nhân viên','Họ tên','CCCD','Điện thoại','Giới tính','Email','Ngày sinh','Phòng ban','Chức vụ','Thâm niên')
    cmbTimNV.current(0)
    cmbTimNV.pack(side=tk.LEFT)

    timnv_entrynv = ttk.Entry(FrameButton,width=10,font = ('Times New Roman',15))
    timnv_entrynv.pack(side=tk.LEFT)
    btnTimNV=tk.Button(FrameButton,text = 'Tìm kiếm',font = ('Times New Roman',15),cursor = 'hand2',command = tim_nv)
    btnTimNV.pack(side=tk.LEFT)
    ttk.Label(FrameButton,width=5).pack(side=tk.LEFT)
    btnTatCa = tk.Button(FrameButton,text = 'Tất cả',font = ('Times New Roman',15),cursor = 'hand2',command = load_data_nv)
    btnTatCa.pack(side=tk.LEFT)

    ttk.Label(FrameButton,width=5).pack(side=tk.LEFT)
    
    btnThoatNV = tk.Button(FrameButton,text = 'Thoát',font = ('Times New Roman',15),cursor = 'hand2',command = thoat_ht)
    btnThoatNV.pack(side=tk.LEFT)
    FrameButton.grid(row=3,column=0,columnspan=7)
    
    ttk.Label(FrametabNhanvien,font = (15)).grid(row=4,column=0)
    ttk.Label(FrametabNhanvien,text = 'Danh sách nhân viên:',font = ('Times New Roman',15)).grid(row=5,column=0)

    columns = ('Mã nhân viên','Họ tên','CCCD','Điện thoại','Giới tính','Email','Ngày sinh','Phòng ban','Chức vụ','Thâm niên')
    tree = ttk.Treeview(FrametabNhanvien,columns = columns,show = "headings",height = 10)

    for col in columns:
        tree.heading(col,text = col.capitalize())

    tree.column('Mã nhân viên',width = 80,anchor = "center")
    tree.column('Họ tên',width=120,anchor="center")
    tree.column('CCCD',width=100,anchor="center")
    tree.column('Điện thoại',width=100,anchor="center")
    tree.column('Giới tính',width=60,anchor="center")
    tree.column('Email',width=130,anchor="center")
    tree.column('Ngày sinh',width=100,anchor="center")
    tree.column('Phòng ban',width=120,anchor="center")
    tree.column('Chức vụ',width=120,anchor="center")
    tree.column('Thâm niên',width=60,anchor="center")

    tree.grid(row=6,column=0,columnspan=7)
    load_data_nv()
    def select_item(event):
        selected_item = tree.focus()
        if selected_item:
            values = tree.item(selected_item, 'values')
            if values:
                clear_input()
                manv_entrynv.insert(0, values[0])    
                tennv_entrynv.insert(0, values[1])  
                cccd_entrynv.insert(0, values[2])     
                dienthoai_entrynv.insert(0,values[3])
                stringGioiTinh.set(values[4])
                mail_entrynv.insert(0,values[5])
                ngaysinh_dateentrynv.set_date(values[6]) 
                cmbPhongBan.set(values[7])
                cmbChucVu.set(values[8])
                thamnien_entrynv.insert(0,values[9])
    FrametabNhanvien.place(x=40,y=20)
    tree.bind('<<TreeviewSelect>>', select_item)

    #=========================================================================================================Tab Hợp Đồng===============
 
    tabHopDong = ttk.Frame(tab_control)
    tab_control.add(tabHopDong,text = "HỢP ĐỒNG")
    FrametabHopdong = tk.Frame(tabHopDong)
    ttk.Label(FrametabHopdong,text = "QUẢN LÝ HỢP ĐỒNG",font = ('Times New Roman',20,'bold')).grid(row=0,column=0,columnspan=7)

    ttk.Label(FrametabHopdong,font = (10)).grid(row=1,column=0)

    lblFrameHD1 = ttk.Frame(FrametabHopdong)
    ttk.Label(lblFrameHD1,text = 'Mã hợp đồng: ',font = ('Times New Roman',15)).pack(side = tk.TOP)
    ttk.Label(lblFrameHD1,font=(10)).pack(side = tk.TOP)
    ttk.Label(lblFrameHD1,text = 'Loại hợp đồng: ',font = ('Times New Roman',15)).pack(side = tk.TOP)
    ttk.Label(lblFrameHD1,font=(10)).pack(side = tk.TOP)
    ttk.Label(lblFrameHD1,text = 'Ngày kí: ',font = ('Times New Roman',15)).pack(side = tk.TOP)
    ttk.Label(lblFrameHD1,font=(10)).pack(side = tk.TOP)
    ttk.Label(lblFrameHD1,text = 'Thời hạn: ',font = ('Times New Roman',15)).pack(side = tk.TOP)
    ttk.Label(lblFrameHD1,font=(10)).pack(side = tk.TOP)
    lblFrameHD1.grid(row=2,column=0)

    ttk.Label(FrametabHopdong,width=10).grid(row=2,column=1)

    FrameHD1 = ttk.Frame(FrametabHopdong)
    stringMaHD = tk.StringVar()
    stringThoiHan = tk.DoubleVar()
    stringLuongCB = tk.StringVar()
    mahd_entryhd = ttk.Entry(FrameHD1,font = ('Times New Roman',15),width=20,textvariable = stringMaHD)
    mahd_entryhd.pack(side=tk.TOP)
    ttk.Label(FrameHD1,font = (10)).pack(side=tk.TOP)

    cmbLoaiHD = ttk.Combobox(FrameHD1,width=20,font = cmb_font)
    cmbLoaiHD['values']=('(Chọn loại hợp đồng)','Thực tập','Ngắn hạn','Dài hạn')
    cmbLoaiHD.current(0)
    cmbLoaiHD.pack(side=tk.TOP)
    ttk.Label(FrameHD1,font = (10)).pack(side=tk.TOP)

    ngayki_dateentryhd = DateEntry(FrameHD1,font = (15),width=15, background="darkblue", foreground="white", date_pattern="yyyy-mm-dd")
    ngayki_dateentryhd.pack(side=tk.TOP)
    ttk.Label(FrameHD1,font=(10)).pack(side = tk.TOP)

    thoihan_entryhd = ttk.Entry(FrameHD1,font = ('Times New Roman',15),width = 20,textvariable = stringThoiHan)
    thoihan_entryhd.pack(side=tk.TOP)
    ttk.Label(FrameHD1,font = (10)).pack(side = tk.TOP)

    FrameHD1.grid(row=2,column=2)

    ttk.Label(FrametabHopdong,width=10).grid(row=2,column=3)

    lblFrameHD2 = ttk.Frame(FrametabHopdong)
    ttk.Label(lblFrameHD2,text = 'Mã nhân viên: ',font = ('Times New Roman',15)).pack(side=tk.TOP)
    ttk.Label(lblFrameHD2,font = (10)).pack(side = tk.TOP)
    ttk.Label(lblFrameHD2,text = 'Ngày bắt đầu: ',font = ('Times New Roman',15)).pack(side=tk.TOP)
    ttk.Label(lblFrameHD2,font = (10)).pack(side = tk.TOP)
    ttk.Label(lblFrameHD2,text = 'Ngày kết thúc: ',font = ('Times New Roman',15)).pack(side=tk.TOP)
    ttk.Label(lblFrameHD2,font = (10)).pack(side = tk.TOP)
    ttk.Label(lblFrameHD2,text = 'Lương cơ bản: ',font = ('Times New Roman',15)).pack(side=tk.TOP)
    ttk.Label(lblFrameHD2,font = (10)).pack(side = tk.TOP)
    lblFrameHD2.grid(row=2,column=4)

    ttk.Label(FrametabHopdong,width=10).grid(row=2,column=5)

    FrameHD2 = ttk.Frame(FrametabHopdong)
    manv_entryhd = ttk.Entry(FrameHD2,font = ('Times New Roman',15),width = 20,textvariable = stringMaNV)
    manv_entryhd.pack(side=tk.TOP)
    ttk.Label(FrameHD2,font = (10)).pack(side = tk.TOP)
    ngaybatdau_dateentryhd = DateEntry(FrameHD2,font =(15),width=15, background="darkblue", foreground="white", date_pattern="yyyy-mm-dd")
    ngaybatdau_dateentryhd.pack(side=tk.TOP)
    ttk.Label(FrameHD2,font = (10)).pack(side=tk.TOP)
    ngayketthuc_dateentryhd = DateEntry(FrameHD2,font = (15),width=15, background="darkblue", foreground="white", date_pattern="yyyy-mm-dd")
    ngayketthuc_dateentryhd.pack(side=tk.TOP)
    ttk.Label(FrameHD2,font = (10)).pack(side=tk.TOP)
    luongcb_entryhd = ttk.Entry(FrameHD2,font = ('Times New Roman',15),width=20,textvariable = stringLuongCB)
    luongcb_entryhd.pack(side=tk.TOP)
    ttk.Label(FrameHD2,font = (10)).pack(side=tk.TOP)
    FrameHD2.grid(row=2,column=6)

    def load_data_hd():
        for i in treehd.get_children():
            treehd.delete(i)
        con = connect_db()
        if con is None: return
        cur = con.cursor()
        try:
            cur.execute('SELECT * FROM HOPDONG')
            for row in cur:
                data_list = list(row)
                for i, item in enumerate(data_list):
                    if isinstance(item, datetime.date):
                        data_list[i] = item.strftime('%Y-%m-%d')
                treehd.insert('', tk.END, values=data_list)
        except Exception as e:
            messagebox.showerror("Lỗi Truy vấn", f"Lỗi khi thực thi truy vấn: {e}")
        con.close()
        clear_input_hd()
    
    def clear_input_hd():
        mahd_entryhd.delete(0,tk.END)
        cmbLoaiHD.current(0)
        ngayki_dateentryhd.set_date(date.today()) 
        thoihan_entryhd.delete(0,tk.END)
        manv_entryhd.delete(0,tk.END)
        ngaybatdau_dateentryhd.set_date(date.today())   
        ngayketthuc_dateentryhd.set_date(date.today())
        luongcb_entryhd.delete(0,tk.END)  
        timhd_entryhd.delete(0,tk.END)  
    
    def them_hd():
        mahd = mahd_entryhd.get()
        loaihd = cmbLoaiHD.get()
        ngayki = ngayki_dateentryhd.get_date() 
        manv = manv_entryhd.get()
        ngaybatdau = ngaybatdau_dateentryhd.get_date()
        ngayketthuc = ngayketthuc_dateentryhd.get_date()
        luongcb = luongcb_entryhd.get()

        if ngayketthuc <= ngaybatdau:
            messagebox.showwarning("thông báo","vui lòng nhập ngày kết thúc hợp đồng phù hợp (sau ngày bắt đầu)")
            return
        #tính thâm niên của nhân viên từ ngày hợp đồng hiệu lực đến này kết thúc hợp đồng
        time_diff = ngayketthuc - ngaybatdau
        thoihan = time_diff.days / 365.25

        if mahd == "" or loaihd == "" or ngayki == "" or manv == "" or ngaybatdau == "" or ngayketthuc == "" or luongcb == "":
            messagebox.showwarning("thiếu dữ liệu","vui lòng nhập đủ thông tin")
            return
            
        if thoihan_entryhd.get().strip() != "":
            messagebox.showwarning("thông báo","không cần nhập thời hạn hợp đồng, hệ thống sẽ tự tính")
            return
            
        try:
            luongcb = float(luongcb)
        except ValueError:
            messagebox.showwarning("Lỗi", "Lương cơ bản phải là số.")
            return

        if len(mahd)!=5 or mahd[0:2]!='HD':
            messagebox.showwarning("thông báo","vui lòng mã hợp đồng 5 kí tự")
            return
        try:
            result = float(mahd[2:])
        except ValueError:
            messagebox.showwarning("Lỗi", "Mã hợp đồng không hợp lệ.")
            return
        
        if loaihd not in ('Thực tập','Ngắn hạn','Dài hạn'):
            messagebox.showwarning("thông báo","vui lòng nhập hoặc chọn lại loại hợp đồng phù hợp")
            return

        if float(luongcb)<=0:
            messagebox.showwarning("thông báo","vui lòng nhập lương cơ bản phù hợp (lớn hơn 0)")
            return
        #ngày kếy thúc hợp đồng phải sau ngày hợp đồng hiệu lực
        if ngayketthuc <= ngaybatdau:
            messagebox.showwarning("thông báo","vui lòng nhập ngày kết thúc hợp đồng phù hợp (sau ngày bắt đầu)")
            return
        #ngày kí không được sau ngày hợp đồng hiệu lực
        if ngayki > ngaybatdau:
            messagebox.showwarning("thông báo","ngày kí không được sau ngày hợp đồng hiệu lực")
            return

        con = connect_db()
        if con is None: return
        cur = con.cursor()
        try:
            #kiểm tra mã nhân viên có đúng nhân viên của công ty hay không
            cur.execute("SELECT COUNT(*) FROM NHANVIEN WHERE MANV=?", (manv,))
            if cur.fetchone()[0] == 0:
                messagebox.showwarning("Lỗi","Mã nhân viên không tồn tại, vui lòng kiểm tra lại")
                return
            #nếu nhập mã nhân viên của giám đốc thì không tạo hợp đồng
            cur.execute("SELECT COUNT(*) FROM NHANVIEN WHERE MANV = ? AND CHUCVU = N'Giám đốc'", (manv,))
            if cur.fetchone()[0] != 0:
                messagebox.showwarning("Lỗi","Không thể tạo hợp đồng cho Giám đốc.")
                return
            #kiểm tra mã hợp đồng mới có nhập trùng với mã hợp đồng trong hệ thống hay không
            cur.execute("SELECT COUNT(*) FROM HOPDONG WHERE MAHD=?", (mahd,))
            if cur.fetchone()[0] > 0:
                messagebox.showwarning("Lỗi","Mã hợp đồng đã tồn tại, vui lòng chọn mã khác")
                return
            #hệ thống chỉ lưu hợp đồng còn thời hạn (nếu hết hạn thì tạo hợp đồng mới)
            #trường hợp nhân viên gia hạn hợp đồng để tiếp tục làm thì tạo hợp đồng mới với ngày hiệu lực của hợp đồng cũ để giữ thâm niên
            today_str = date.today().strftime('%Y-%m-%d')
            cur.execute("SELECT COUNT(*) FROM HOPDONG WHERE MANV=? AND NGAY_HET_HAN >= ?", (manv, today_str))
            if cur.fetchone()[0] > 0:
                messagebox.showwarning("Lỗi","Nhân viên này đang có hợp đồng còn thời hạn, không thể tạo thêm hợp đồng mới")
                return
            #nếu mã nhân viên đã có tồn tại hợp đồng cũ đã hết hạn thì lấy ngày hết hạn của hợp đồng để đối chiếu
            cur.execute("SELECT MAX(NGAY_HET_HAN) FROM HOPDONG WHERE MANV = ?",(manv,))
                #nếu ngày hết hạn hợp đồng cũ với ngày bắt đầu hợp đồng mới trong khoảng 1 tuần thì lấy thâm niên hợp đồng cũ 
            ngayhethan = cur.fetchone()[0]
            if ngayhethan is not None:
                if ngaybatdau < ngayhethan:
                    messagebox.showwarning("thông báo","không thể tạo hợp đồng mới trong khi hợp đồng khác còn hiệu lực")
                    return
                if (ngaybatdau - ngayhethan).days >=0 and (ngaybatdau - ngayhethan).days <= 7:
                    ngaythamnien = ngayhethan
                else:
                    ngaythamnien = ngaybatdau
            else:
                ngaythamnien = ngaybatdau

            #giới hạn loại hợp đồng theo thời hạn làm việc
            if thoihan < 0.5 and loaihd != 'Thực tập':
                messagebox.showwarning("Lỗi","Thời hạn dưới 6 tháng phải là hợp đồng Thực tập")
                cmbLoaiHD.set("Thực tập")
                return
            elif thoihan >= 0.5 and thoihan < 2 and loaihd != 'Ngắn hạn':
                messagebox.showwarning("Lỗi","Thời hạn từ 6 tháng đến dưới 2 năm phải là hợp đồng Ngắn hạn")
                cmbLoaiHD.set("Ngắn hạn")
                return
            elif thoihan >= 2 and loaihd != 'Dài hạn':
                messagebox.showwarning("Lỗi","Thời hạn từ 2 năm trở lên phải là hợp đồng Dài hạn")
                cmbLoaiHD.set("Dài hạn")
                return
            #yêu cầu lương cơ bản phù hợp với thời hạn hợp đồng
            if loaihd == 'Thực tập' and luongcb > 20000:
                messagebox.showwarning("Lỗi","Hợp đồng thực tập có lương cơ bản không được vượt quá 20,000, vui lòng kiểm tra lại")
                return
            if loaihd == 'Ngắn hạn' and (luongcb <20000 or luongcb >50000):
                messagebox.showwarning("Lỗi","Hợp đồng ngắn hạn có lương cơ bản từ 20,000 đến 50,000, vui lòng kiểm tra lại")
                return

            if loaihd == 'Dài hạn' and luongcb <50000:
                messagebox.showwarning("Lỗi","Hợp đồng dài hạn có lương cơ bản phải từ 50,000 trở lên, vui lòng kiểm tra lại")
                return
            #kiểm tra mã hợp đồng
            cur.execute("SELECT COUNT(*) FROM HOPDONG WHERE MAHD = ?",(mahd))
            if cur.fetchone()[0]!=0:
                messagebox.showwarning("thông báo","mã hợp đồng đã tồn tại, vui lòng nhập mã hợp đồng khác")
                return
            
            cur.execute("INSERT INTO HOPDONG VALUES (?,?,?,?,?,?,?,?)", (mahd, loaihd, ngayki, thoihan, manv, ngaybatdau, ngayketthuc, luongcb))
            #cập nhật thâm niên cho nhân viên
            tn = int(date.today().year - ngaythamnien.year)
            cur.execute("UPDATE NHANVIEN SET THAMNIEN = ? WHERE MANV = ?", (tn, manv))
            
            con.commit()
            messagebox.showinfo("Thành công", "Đã thêm hợp đồng thành công.")
            
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
        con.close()
        load_data_hd()

    def xoa_hd():
        selected = treehd.selection() 
        if not selected: 
            messagebox.showwarning("Chưa chọn", "Hãy chọn hợp đồng để xóa") 
            return 
        mahd = treehd.item(selected)["values"][0] 
        con = connect_db() 
        cur = con.cursor() 
        #không xóa hợp đồng còn thời hạn
        today_str = date.today().strftime('%Y-%m-%d')
        cur.execute("SELECT COUNT(*) FROM HOPDONG WHERE MAHD=? AND NGAY_HET_HAN >= ?", (mahd, today_str))
        if cur.fetchone()[0] > 0:
            messagebox.showwarning("Lỗi","Nhân viên này đang có hợp đồng còn thời hạn, không thể tạo thêm hợp đồng mới")
            return
        #chắc chắn mã hợp đồng đã tồn tại để xóa
        cur.execute("SELECT COUNT(*) FROM HOPDONG WHERE MAHD = ?",(mahd,))
        if cur.fetchone()[0]==0:
            messagebox.showwarning("thông báo","mã hợp đồng không tồn tại, vui lòng chọn hợp đồng để xóa")
            return
        cur.execute("SELECT COUNT(*) FROM CONG_NGAY WHERE MANV IN (SELECT MANV FROM HOPDONG WHERE MAHD = ?)",(mahd,))
        if cur.fetchone()[0]!=0:
            messagebox.showwarning("thông báo","thông tin nhân viên còn lưu công ngày, không thể xóa hợp đồng")
            return
        cur.execute("SELECT COUNT(*) FROM LUONG WHERE MANV IN (SELECT MANV FROM HOPDONG WHERE MAHD = ?)",(mahd,))
        if cur.fetchone()[0]!=0:
            messagebox.showwarning("thông báo","thông tin nhân viên còn lưu lương, không thể xóa hợp đồng")
            return
        
        cur.execute("DELETE FROM HOPDONG WHERE MAHD=?", (mahd,)) 
        #nếu mã nhân viên không còn hợp đồng còn hạn thì cập nhật thâm niên là 0
        #chỉ giữ thâm niên cũ nếu không xóa hợp đồng cũ và tạo liền hợp đồng mới
        cur.execute("UPDATE NHANVIEN SET THAMNIEN = 0 WHERE MANV NOT IN (SELECT MANV FROM HOPDONG WHERE NGAY_HET_HAN >= ?)", (date.today(),))
        con.commit() 
        con.close() 
        load_data_hd()

    def sua_hd():
        selected = treehd.selection() 
        if not selected: 
            messagebox.showwarning("Chưa chọn", "Hãy chọn nhân viên để sửa") 
            return 
        luu_hd()

    def luu_hd():
        mahd = mahd_entryhd.get()
        manv = manv_entryhd.get()
        luongcb = luongcb_entryhd.get()
        con = connect_db() 
        cur = con.cursor() 
        tb = messagebox.askyesno("Xác nhận","bạn có chắc chắn muốn sửa hợp đồng này không?")

        if tb>0:
            if mahd == "" or manv == ""  or luongcb == "":
                messagebox.showwarning("thiếu dữ liệu","vui lòng nhập đủ thông tin")
                return
                
            try:
                luongcb = float(luongcb)
            except ValueError:
                messagebox.showwarning("Lỗi", "Lương cơ bản phải là số.")
                return

            if len(mahd)!=5 or mahd[0:2]!='HD':
                messagebox.showwarning("thông báo","vui lòng mã hợp đồng 5 kí tự")
                return
            #sửa hợp đồng với mã nhân viên có tồn tại
            cur.execute("SELECT COUNT(*) FROM NHANVIEN WHERE MANV=?", (manv,))
            if cur.fetchone()[0] == 0:
                messagebox.showwarning("Lỗi","Mã nhân viên không tồn tại, vui lòng kiểm tra lại")
                return
            #không đổi hợp đồng gán cho giám đốc
            cur.execute("SELECT COUNT(*) FROM NHANVIEN WHERE MANV = ? AND CHUCVU = N'Giám đốc'", (manv,))
            if cur.fetchone()[0] != 0:
                messagebox.showwarning("Lỗi","Không thể tạo hợp đồng cho Giám đốc.")
                return
            #chỉ sửa hợp đồng đã tồn tại 
            cur.execute("SELECT COUNT(*) FROM HOPDONG WHERE MAHD=?", (mahd,))
            if cur.fetchone()[0] == 0:
                messagebox.showwarning("Lỗi","Mã hợp đồng không tồn tại, vui lòng kiểm tra lại")
                return
            tb = messagebox.askyesno("thông báo","bạn có muốn sửa thông tin hợp đồng không? (chỉ sửa được lương cơ bản, mã nhân viên)")
            cur.execute("""UPDATE HOPDONG SET MANV = ?,LUONGCB=? WHERE MAHD = ?""", (manv,luongcb,mahd)) 
        con.commit() 
        con.close() 
        load_data_hd() 

    def load_data_timhd(string):
        for i in treehd.get_children():
            treehd.delete(i)
        con = connect_db()
        if con is None: return
        cur = con.cursor()
        try:
            cur.execute(string)
            for row in cur:
                data_list = list(row)
                for i, item in enumerate(data_list):
                    if isinstance(item, datetime.date):
                        data_list[i] = item.strftime('%Y-%m-%d')
                treehd.insert('', tk.END, values=data_list)
        except Exception as e:
            messagebox.showerror("Lỗi Truy vấn", f"Lỗi khi thực thi truy vấn: {e}")
        con.close()

    def tim_hd():
        tim = cmbTimHD.get()
        if (tim == 'Mã hợp đồng'):
            mahd = timhd_entryhd.get()
            load_data_timhd("SELECT * FROM HOPDONG WHERE MAHD='"+mahd+"'")
        elif (tim == 'Loại hợp đồng'):
            loaihd = timhd_entryhd.get()
            load_data_timhd("SELECT * FROM HOPDONG WHERE LOAIHD LIKE N'%"+loaihd+"%'")
        elif (tim == 'Mã nhân viên'):
            manv = timhd_entryhd.get()
            load_data_timhd("SELECT * FROM HOPDONG WHERE MANV='"+manv+"'")
        elif (tim == 'Thời hạn'):
            thoihan = timhd_entryhd.get()
            load_data_timhd("SELECT * FROM HOPDONG WHERE THOIHAN='"+thoihan+"'")
        else:
            messagebox.showwarning("thông báo","vui lòng chọn đúng danh mục tìm kiếm")
            return      

    FrameButtonHD = ttk.Frame(FrametabHopdong)
    ttk.Label(FrameButtonHD,width=5).pack(side=tk.LEFT)
    btnThemHD=tk.Button(FrameButtonHD,text = 'Thêm',font = ('Times New Roman',15),cursor = 'hand2',command = them_hd)
    btnThemHD.pack(side=tk.LEFT)
    ttk.Label(FrameButtonHD,width=5).pack(side=tk.LEFT)
    btnXoaHD=tk.Button(FrameButtonHD,text = 'Xóa',font = ('Times New Roman',15),cursor = 'hand2',command = xoa_hd)
    btnXoaHD.pack(side=tk.LEFT)
    ttk.Label(FrameButtonHD,width=5).pack(side=tk.LEFT)
    btnHuyHD=tk.Button(FrameButtonHD,text = 'Hủy',font = ('Times New Roman',15),cursor = 'hand2',command = clear_input_hd)
    btnHuyHD.pack(side=tk.LEFT)
    ttk.Label(FrameButtonHD,width=5).pack(side=tk.LEFT)
    btnSuaHD=tk.Button(FrameButtonHD,text = 'Sửa',font=('Times New Roman',15),cursor = 'hand2',command = sua_hd)
    btnSuaHD.pack(side=tk.LEFT)
    ttk.Label(FrameButtonHD,width=5).pack(side=tk.LEFT)
    cmbTimHD = ttk.Combobox(FrameButtonHD,width=20,font=cmb_font)
    cmbTimHD['values'] = ('Mã hợp đồng','Loại hợp đồng','Mã nhân viên','Thời hạn')
    cmbTimHD.current(0)
    cmbTimHD.pack(side=tk.LEFT)

    timhd_entryhd = ttk.Entry(FrameButtonHD,width=20,font = ('Times New Roman',15))
    timhd_entryhd.pack(side=tk.LEFT)
    btnTimHD=tk.Button(FrameButtonHD,text = 'Tìm',font = ('Times New Roman',15),cursor = 'hand2',command = tim_hd)
    btnTimHD.pack(side=tk.LEFT)
    ttk.Label(FrameButtonHD,width=5).pack(side=tk.LEFT)
    btnTatCaHD = tk.Button(FrameButtonHD,text = 'Tất cả',font = ('Times New Roman',15),cursor = 'hand2',command = load_data_hd)
    btnTatCaHD.pack(side=tk.LEFT)
    ttk.Label(FrameButtonHD,width=5).pack(side=tk.LEFT)
    btnThoatHD = tk.Button(FrameButtonHD,text = 'Thoát',font = ('Times New Roman',15),cursor = 'hand2',command = thoat_ht)
    btnThoatHD.pack(side=tk.LEFT)

    FrameButtonHD.grid(row=3,column=0,columnspan=7)
    
    ttk.Label(FrametabHopdong,font = (15)).grid(row=4,column=0)
    ttk.Label(FrametabHopdong,text = 'Danh sách hợp đồng:',font = ('Times New Roman',15)).grid(row=5,column=0)

    columns = ("Mã hợp đồng","Loại hợp đồng","Ngày kí","Thời hạn","Mã nhân viên","Ngày bắt đầu","Ngày kết thúc","Lương cơ bản")
    treehd = ttk.Treeview(FrametabHopdong,columns = columns,show = "headings",height = 10)

    for col in columns:
        treehd.heading(col,text = col.capitalize())

    treehd.column("Mã hợp đồng",width = 60,anchor = "center")
    treehd.column("Loại hợp đồng",width=120,anchor="center")
    treehd.column("Ngày kí",width=120,anchor="center")
    treehd.column("Thời hạn",width=60,anchor="center")
    treehd.column("Mã nhân viên",width=60,anchor="center")
    treehd.column("Ngày bắt đầu",width=120,anchor="center")
    treehd.column("Ngày kết thúc",width=120,anchor="center")
    treehd.column("Lương cơ bản",width=120,anchor="center")

    treehd.grid(row=6,column=0,columnspan=7)
    load_data_hd()

    def select_item_hd(event):
        selected_item = treehd.focus()
        if selected_item:
            values = treehd.item(selected_item, 'values')
            if values:
                clear_input_hd()
                mahd_entryhd.insert(0, values[0])    
                cmbLoaiHD.set(values[1])  
                ngayki_dateentryhd.set_date(values[2]) 
                thoihan_entryhd.insert(0, f"{float(values[3]):.1f}")     
                manv_entryhd.insert(0,values[4])
                ngaybatdau_dateentryhd.set_date(values[5]) 
                ngayketthuc_dateentryhd.set_date(values[6]) 
                luongcb_entryhd.insert(0,f"{float(values[7]):,.0f}VND")
    FrametabHopdong.place(x=10,y=20)
    treehd.bind('<<TreeviewSelect>>', select_item_hd)

    #=================================================================================================Chấm công ngày====================
    tabCongNgay = ttk.Frame(tab_control)
    tab_control.add(tabCongNgay,text = "CÔNG NGÀY")
    FrametabCongngay = tk.Frame(tabCongNgay)
    ttk.Label(FrametabCongngay,text = "CHẤM CÔNG NGÀY",font = ('Times New Roman',20,'bold')).grid(row=0,column=0,columnspan=7)

    ttk.Label(FrametabCongngay,font = (10)).grid(row=1,column=0,columnspan=7)

    lblFrameCN1 = ttk.Frame(FrametabCongngay)
    ttk.Label(lblFrameCN1,text = "Mã nhân viên: ",font = ('Times New Roman',15)).pack(side=tk.TOP)
    ttk.Label(lblFrameCN1,font = (10)).pack(side=tk.TOP)
    ttk.Label(lblFrameCN1,text = "Ngày làm: ",font = ('Times New Roman',15)).pack(side=tk.TOP)
    ttk.Label(lblFrameCN1,font = (10)).pack(side=tk.TOP)
    lblFrameCN1.grid(row=2,column=0)

    ttk.Label(FrametabCongngay,width=10).grid(row=2,column=1)

    FrameCN1 = ttk.Frame(FrametabCongngay)
    manv_entrycn = ttk.Entry(FrameCN1,font = (15),width=20,textvariable = stringMaNV)
    manv_entrycn.pack(side=tk.TOP)
    ttk.Label(FrameCN1,font = (10)).pack(side=tk.TOP)
    ngaylam_dateentrycn = DateEntry(FrameCN1,font = (15),width=15, background="darkblue", foreground="white", date_pattern="yyyy-mm-dd")
    ngaylam_dateentrycn.pack(side=tk.TOP)
    ttk.Label(FrameCN1,font = (10)).pack(side=tk.TOP)
    FrameCN1.grid(row=2,column=2)

    ttk.Label(FrametabCongngay,width=10).grid(row=2,column=3)

    lblFrameCN2 = ttk.Frame(FrametabCongngay)
    ttk.Label(lblFrameCN2,text = "Số giờ chính: ",font = ('Times New Roman',15)).pack(side=tk.TOP)
    ttk.Label(lblFrameCN2,font = (10)).pack(side=tk.TOP)
    ttk.Label(lblFrameCN2,text = "Số giờ tăng ca: ",font = ('Times New Roman',15)).pack(side=tk.TOP)
    lblFrameCN2.grid(row=2,column=4)

    ttk.Label(FrametabCongngay,width=10).grid(row=2,column=5)

    FrameCN2 = ttk.Frame(FrametabCongngay)
    stringGioLam = tk.DoubleVar()
    stringTangCa = tk.DoubleVar()
    giolam_entrycn = ttk.Entry(FrameCN2,font = (15),width=20,textvariable = stringGioLam)
    giolam_entrycn.pack(side=tk.TOP)
    ttk.Label(FrameCN2,font = (10)).pack(side=tk.TOP)
    tangca_entrycn = ttk.Entry(FrameCN2,font = (15),width=20,textvariable = stringTangCa)
    tangca_entrycn.pack(side=tk.TOP)
    ttk.Label(FrameCN2,font = (10)).pack(side=tk.TOP)
    FrameCN2.grid(row=2,column=6)

    def load_data_cn():
        for i in treecn.get_children():
            treecn.delete(i)
        con = connect_db()
        if con is None: return
        cur = con.cursor()
        try:
            cur.execute('SELECT * FROM CONG_NGAY')
            for row in cur:
                data_list = list(row)
                for i, item in enumerate(data_list):
                    if isinstance(item, datetime.date):
                        data_list[i] = item.strftime('%Y-%m-%d')
                treecn.insert('', tk.END, values=data_list)
        except Exception as e:
            messagebox.showerror("Lỗi Truy vấn", f"Lỗi khi thực thi truy vấn: {e}")
        con.close()
        clear_input_cn()

    def clear_input_cn():
        manv_entrycn.delete(0,tk.END)
        ngaylam_dateentrycn.set_date(date.today())
        giolam_entrycn.delete(0,tk.END)
        tangca_entrycn.delete(0,tk.END)
        timcn_entrycn.delete(0,tk.END)

    def them_cn():
        manv = manv_entrycn.get()
        ngaylam = ngaylam_dateentrycn.get_date()
        giolam = int(giolam_entrycn.get())
        tangca = int(tangca_entrycn.get())
        if manv == "" or ngaylam == "" or giolam_entrycn.get() == "" or tangca_entrycn.get() == "":
            messagebox.showwarning("thiếu dữ liệu","vui lòng nhập đủ thông tin")
            return
        #giờ làm chính chỉ tối đa 8 tiếng
        if giolam<0 or giolam>8:
            messagebox.showwarning("thông báo","vui lòng nhập số giờ làm phù hợp (lớn hơn hoặc bằng 0 và nhỏ hơn hoặc bằng 8)")
            return
        #tăng ca tối đa 4 tiếng
        if tangca<0 or tangca>4:
            messagebox.showwarning("thông báo","vui lòng nhập số giờ tăng ca phù hợp (lớn hơn hoặc bằng 0 và nhỏ hơn hoặc bằng 4)")
            return
        #mã nhân viên đúng định dạng
        if len(manv)!=5 or manv[0:2]!='NV':
            messagebox.showwarning("thông báo","vui lòng mã nhân viên 5 kí tự")
            return
        try:
            result = float(manv[2:])
        except ValueError:
            messagebox.showwarning("Lỗi", "Mã nhân viên không hợp lệ")
            return
        #không nhập công cho ngày sau ngày nhập
        if ngaylam > date.today():
            messagebox.showwarning("thông báo","vui lòng nhập ngày làm phù hợp (không được sau ngày hiện tại)")
            return
        
        con = connect_db()
        cur = con.cursor()
        try:
            #mã nhân viên phải tồn tại hoặc có hợp đồng còn hạn mới được chấm công
            cur.execute("""SELECT COUNT(*) FROM NHANVIEN WHERE (MANV NOT IN (SELECT MANV FROM HOPDONG) 
                           OR MANV NOT IN (SELECT MANV FROM HOPDONG WHERE NGAY_HET_HAN >= ?)) AND MANV = ?""", (date.today(),manv))
            if cur.fetchone()[0] > 0:
                messagebox.showwarning("Lỗi","Không thể chấm công cho nhân viên không có hợp đồng hoặc hợp đồng đã hết hạn.")
                return
            #ngoài thời gian hợp đồng thì không được nhập công
            cur.execute("""SELECT COUNT(*) FROM HOPDONG WHERE MANV = ? AND (NGAY_HIEU_LUC > ? OR NGAY_HET_HAN < ?) 
                           AND MAHD IN (SELECT MAHD FROM HOPDONG WHERE NGAY_HET_HAN >= ?)""",(manv,ngaylam,ngaylam,date.today()))
            if cur.fetchone()[0] > 0:
                messagebox.showwarning("thông báo","ngày công nằm ngoài giới hạn hợp đồng của nhân viên này")
                return
            #giám đốc không có hợp đồng nên không chấm công
            cur.execute("SELECT COUNT(*) FROM NHANVIEN WHERE CHUCVU = 'Giám đốc' AND MANV = ?", (manv,))
            if cur.fetchone()[0] > 0:
                messagebox.showwarning("Lỗi","Không thể chấm công cho Giám đốc.")
                return
            #nếu đã chấm công cùng ngày thì không cho nhập lần thứ 2
            cur.execute("SELECT COUNT(*) FROM CONG_NGAY WHERE MANV = ? AND NGAYLAM = ?", (manv,ngaylam))
            if cur.fetchone()[0] > 0:
                messagebox.showwarning("trùng dữ liệu","nhân viên đã được chấm công trong ngày này rồi")
                return
            cur.execute("INSERT INTO CONG_NGAY (MANV,NGAYLAM,GIOCHINH,TANGCA) VALUES (?,?,?,?)", (manv,ngaylam,giolam,tangca))
                
            con.commit()
        except Exception as e:
            messagebox.showerror("Lỗi", str(e))
        con.close()
        load_data_cn()

    def xoa_cn():
        selected = treecn.selection() 
        if not selected: 
            messagebox.showwarning("Chưa chọn", "Hãy chọn nhân viên để xóa")
            return
        manv = treecn.item(selected)["values"][0]
        ngaylam = treecn.item(selected)["values"][1]
        con = connect_db()
        cur = con.cursor()
        #đã được tính lương vì để tính lương phải tổng hợp giờ làm để tính lương nên không xóa
        cur.execute("SELECT COUNT(*) FROM LUONG L,CONG_NGAY CN WHERE L.MANV = ? AND L.THANG = FORMAT(CN.NGAYLAM, 'MM/yyyy')",(manv,))
        if cur.fetchone()[0] != 0:
            messagebox.showwarning("thông báo","ngày công này đã được tính lương, không thể xóa được")
            return
        cur.execute("DELETE FROM CONG_NGAY WHERE MANV=? AND NGAYLAM = ?", (manv,ngaylam))
        con.commit()
        con.close()
        load_data_cn()

    def sua_cn():
        selected = treecn.selection() 
        if not selected: 
            messagebox.showwarning("Chưa chọn", "Hãy chọn công ngày để sửa") 
            return 
        luu_cn()

    def luu_cn():
        manv = manv_entrycn.get()
        giolam = int(giolam_entrycn.get())
        tangca = int(tangca_entrycn.get())
        ngaylam = ngaylam_dateentrycn.get_date()
        if manv == "" or ngaylam == "" or giolam_entrycn.get() == "" or tangca_entrycn.get() == "":
            messagebox.showwarning("thiếu dữ liệu","vui lòng nhập đủ thông tin")
            return
        #giờ làm chính chỉ tối đa 8 tiếng
        if giolam<0 or giolam>8:
            messagebox.showwarning("thông báo","vui lòng nhập số giờ làm phù hợp (lớn hơn hoặc bằng 0 và nhỏ hơn hoặc bằng 8)")
            return
        #tăng ca tối đa 4 tiếng
        if tangca<0 or tangca>4:
            messagebox.showwarning("thông báo","vui lòng nhập số giờ tăng ca phù hợp (lớn hơn hoặc bằng 0 và nhỏ hơn hoặc bằng 4)")
            return
        #mã nhân viên đúng định dạng
        if len(manv)!=5 or manv[0:2]!='NV':
            messagebox.showwarning("thông báo","vui lòng mã nhân viên 5 kí tự")
            return
        try:
            result = float(manv[2:])
        except ValueError:
            messagebox.showwarning("Lỗi", "Mã nhân viên không hợp lệ")
            return
        #không nhập công cho ngày sau ngày nhập
        if ngaylam > date.today():
            messagebox.showwarning("thông báo","vui lòng nhập ngày làm phù hợp (không được sau ngày hiện tại)")
            return
        
        con = connect_db() 
        cur = con.cursor()
        #đã tính lương nên không được sửa thông tin công ngày của tháng đó
        cur.execute("SELECT COUNT(*) FROM LUONG L,CONG_NGAY CN WHERE L.MANV = ? AND L.THANG = FORMAT(CN.NGAYLAM, 'MM/yyyy')",(manv,))
        if cur.fetchone()[0] != 0:
            messagebox.showwarning("thông báo","ngày công này đã được tính lương, không thể sửa được")
            return
        cur.execute("""UPDATE CONG_NGAY SET GIOCHINH = ?,TANGCA = ? WHERE MANV = ? AND NGAYLAM = ?""", (giolam,tangca,manv,ngaylam))
        con.commit()
        con.close() 
        load_data_cn()

    def load_data_timcn(string):
        for i in treecn.get_children():
            treecn.delete(i)
        con = connect_db()
        if con is None: return
        cur = con.cursor()
        try:
            cur.execute(string)
            for row in cur:
                data_list = list(row)
                for i, item in enumerate(data_list):
                    if isinstance(item, datetime.date):
                        data_list[i] = item.strftime('%Y-%m-%d')
                treecn.insert('', tk.END, values=data_list)
        except Exception as e:
            messagebox.showerror("Lỗi Truy vấn", f"Lỗi khi thực thi truy vấn: {e}")
        con.close()
        

    def tim_cn():
        tim = cmbTimCN.get()
        if (tim == 'Mã nhân viên'):
            manv = timcn_entrycn.get()
            load_data_timcn("SELECT * FROM CONG_NGAY WHERE MANV='"+manv+"'")
        elif (tim == 'Ngày làm'):
            load_data_timcn("SELECT * FROM CONG_NGAY WHERE NGAYLAM='"+timcn_entrycn.get()+"'")
        else:
            messagebox.showwarning("thông báo","vui lòng chọn đúng danh mục tìm kiếm")
            return

    #tạo hàng nút
    FrameButtonCN = ttk.Frame(FrametabCongngay)
    ttk.Label(FrameButtonCN,width=5).pack(side=tk.LEFT)
    btnThemCN=tk.Button(FrameButtonCN,text = 'Thêm',font = ('Times New Roman',15),cursor = 'hand2',command = them_cn)
    btnThemCN.pack(side=tk.LEFT)
    ttk.Label(FrameButtonCN,width=5).pack(side=tk.LEFT)
    btnXoaCN=tk.Button(FrameButtonCN,text = 'Xóa',font = ('Times New Roman',15),cursor = 'hand2',command = xoa_cn)
    btnXoaCN.pack(side=tk.LEFT)
    ttk.Label(FrameButtonCN,width=5).pack(side=tk.LEFT)
    btnSuaCN=tk.Button(FrameButtonCN,text = 'Sửa',font=('Times New Roman',15),cursor = 'hand2',command = sua_cn)
    btnSuaCN.pack(side=tk.LEFT)
    ttk.Label(FrameButtonCN,width=5).pack(side=tk.LEFT)
    btnHuyCN=tk.Button(FrameButtonCN,text = 'Hủy',font=('Times New Roman',15),cursor = 'hand2',command = clear_input_cn)
    btnHuyCN.pack(side=tk.LEFT)
    ttk.Label(FrameButtonCN,width=5).pack(side=tk.LEFT)
    cmbTimCN = ttk.Combobox(FrameButtonCN,width=20,font=cmb_font)
    cmbTimCN['values'] = ('Mã nhân viên','Ngày làm')
    cmbTimCN.current(0)
    cmbTimCN.pack(side=tk.LEFT)

    timcn_entrycn = ttk.Entry(FrameButtonCN,width=20,font = ('Times New Roman',15))
    timcn_entrycn.pack(side=tk.LEFT)
    btnTimCN=tk.Button(FrameButtonCN,text = 'Tìm',font = ('Times New Roman',15),cursor = 'hand2',command = tim_cn)
    btnTimCN.pack(side=tk.LEFT)
    ttk.Label(FrameButtonCN,width=5).pack(side=tk.LEFT)
    btnTatCaCN = tk.Button(FrameButtonCN,text = 'Tất cả',font = ('Times New Roman',15),cursor = 'hand2',command = load_data_cn)
    btnTatCaCN.pack(side=tk.LEFT)
    ttk.Label(FrameButtonCN,width=5).pack(side=tk.LEFT)
    btnThoatCN = tk.Button(FrameButtonCN,text = 'Thoát',font = ('Times New Roman',15),cursor = 'hand2',command = thoat_ht)
    btnThoatCN.pack(side=tk.LEFT)

    FrameButtonCN.grid(row=3,column=0,columnspan=7)
    
    ttk.Label(FrametabCongngay,font = (15)).grid(row=4,column=0)
    ttk.Label(FrametabCongngay,text = 'Danh sách hợp đồng:',font = ('Times New Roman',15)).grid(row=5,column=0)
    ttk.Label(FrametabCongngay,font=(10)).grid(row=6,column=0)

    #tạo danh sách chấm công ngày bằng treeview
    columns = ("Mã nhân viên","Ngày làm","Số giờ chính","Số giờ tăng ca")
    treecn = ttk.Treeview(FrametabCongngay,columns = columns,show = "headings",height = 10)

    for col in columns:
        treecn.heading(col,text = col.capitalize())

    treecn.column("Mã nhân viên",width = 120,anchor = "center")
    treecn.column("Ngày làm",width=180,anchor="center")
    treecn.column("Số giờ chính",width=200,anchor="center")
    treecn.column("Số giờ tăng ca",width=200,anchor="center")
    
    treecn.grid(row=7,column=0,columnspan=7)
    load_data_cn()
    def select_item_cn(event):
        selected_item = treecn.focus()
        if selected_item:
            values = treecn.item(selected_item, 'values')
            if values:
                clear_input_cn()
                manv_entrycn.insert(0, values[0])    
                ngaylam_dateentrycn.set_date(values[1])  
                giolam_entrycn.insert(0, values[2])     
                tangca_entrycn.insert(0,values[3])
    FrametabCongngay.place(x=10,y=20)
    treecn.bind('<<TreeviewSelect>>', select_item_cn)

    #======================================================================================================Chấm công tháng========================
    tabLuong = ttk.Frame(tab_control)
    tab_control.add(tabLuong,text = "LƯƠNG")
    FrametabLuong = tk.Frame(tabLuong)
    ttk.Label(FrametabLuong,text = "QUẢN LÝ LƯƠNG",font = ('Times New Roman',20,'bold')).grid(row=0,column=0,columnspan=7)

    ttk.Label(FrametabLuong,font = (10)).grid(row=1,column=0,columnspan=7)

    lblFrameLuong1 = ttk.Frame(FrametabLuong)
    ttk.Label(lblFrameLuong1,text = 'Mã nhân viên: ',font = ('Times New Roman',15)).pack(side=tk.TOP)
    ttk.Label(lblFrameLuong1,font = (10)).pack(side=tk.TOP)
    ttk.Label(lblFrameLuong1,text = 'Tháng/Năm: ',font = ('Times New Roman',15)).pack(side=tk.TOP)

    ttk.Label(lblFrameLuong1,font = (10)).pack(side=tk.TOP)
    stringTongGio = tk.IntVar()
    stringTongTang = tk.IntVar()
    ttk.Label(lblFrameLuong1,text = "Tổng giờ chính: ",font=('Times New Roman',15)).pack(side=tk.TOP)
    ttk.Label(lblFrameLuong1,font = (10)).pack(side=tk.TOP)
    ttk.Label(lblFrameLuong1,text = "Tổng giờ tăng ca: ",font = ('Times New Roman',15)).pack(side = tk.TOP)
    ttk.Label(lblFrameLuong1,font=(10)).pack(side=tk.TOP)

    lblFrameLuong1.grid(row=2,column=0)

    ttk.Label(FrametabLuong,width=10).grid(row=2,column=1)

    FrameLuong1 = ttk.Frame(FrametabLuong)
    manv_entryluong = ttk.Entry(FrameLuong1,font=(15),width=20,textvariable = stringMaNV)
    manv_entryluong.pack(side=tk.TOP)
    ttk.Label(FrameLuong1,font = (10)).pack(side=tk.TOP)
    stringThang = tk.StringVar()
    thang_entryluong = ttk.Entry(FrameLuong1,font = (15),width=15,textvariable = stringThang)
    thang_entryluong.pack(side=tk.TOP)
    ttk.Label(FrameLuong1,font=(10)).pack(side=tk.TOP)
    tonggio_entryluong = ttk.Entry(FrameLuong1,font = (15),width=15,textvariable = stringTongGio)
    tonggio_entryluong.pack(side=tk.TOP)
    ttk.Label(FrameLuong1,font = (10)).pack(side=tk.TOP)
    tongtang_entryluong = ttk.Entry(FrameLuong1,font = (15),width=15,textvariable = stringTongTang)
    tongtang_entryluong.pack(side=tk.TOP)
    ttk.Label(FrameLuong1,font=(10)).pack(side=tk.TOP)

    FrameLuong1.grid(row=2,column=2)

    ttk.Label(FrametabLuong,width=10).grid(row=2,column=3)

    lblFrameLuong2 = ttk.Frame(FrametabLuong)
    ttk.Label(lblFrameLuong2,text = "Tổng lương: ",font=('Times New Roman',15)).pack(side=tk.TOP)
    ttk.Label(lblFrameLuong2,font = (10)).pack(side=tk.TOP)
    ttk.Label(lblFrameLuong2,text = "Phụ cấp: ",font = ('Times New Roman',15)).pack(side=tk.TOP)
    ttk.Label(lblFrameLuong2,font = (10)).pack(side=tk.TOP)
    ttk.Label(lblFrameLuong2,text = "Khấu trừ: ",font = ('Times New Roman',15)).pack(side=tk.TOP)
    ttk.Label(lblFrameLuong2,font = (10)).pack(side=tk.TOP)
    ttk.Label(lblFrameLuong2,text = "Thực nhận: ",font = ('Times New Roman',15)).pack(side=tk.TOP)
    ttk.Label(lblFrameLuong2,font = (10)).pack(side=tk.TOP)
    lblFrameLuong2.grid(row=2,column=4)

    ttk.Label(FrametabLuong,width=10).grid(row=2,column=5)

    FrameLuong2 = ttk.Frame(FrametabLuong)
    tongluong_entryluong = ttk.Entry(FrameLuong2,font = (15),width=20)
    tongluong_entryluong.pack(side=tk.TOP)
    ttk.Label(FrameLuong2,font=(10)).pack(side=tk.TOP)
    phucap_entryluong = ttk.Entry(FrameLuong2,font=(15),width=20)
    phucap_entryluong.pack(side=tk.TOP)
    ttk.Label(FrameLuong2, font=(10)).pack(side=tk.TOP)
    khautru_entryluong = ttk.Entry(FrameLuong2,font = (15),width=20)
    khautru_entryluong.pack(side=tk.TOP)
    ttk.Label(FrameLuong2,font=(10)).pack(side=tk.TOP)
    thucnhan_entryluong = ttk.Entry(FrameLuong2,font = (15),width=20)
    thucnhan_entryluong.pack(side=tk.TOP)
    ttk.Label(FrameLuong2,font=(10)).pack(side=tk.TOP)
    FrameLuong2.grid(row=2,column=6)

    def load_data_luong():
        for i in treeluong.get_children():
            treeluong.delete(i)
        con = connect_db()
        if con is None: return
        cur = con.cursor()
        try:
            cur.execute('SELECT * FROM LUONG')
            for row in cur:
                data_list = list(row)
                for i, item in enumerate(data_list):
                    if isinstance(item, datetime.date):
                        data_list[i] = item.strftime('%Y-%m-%d')
                treeluong.insert('', tk.END, values=data_list)
        except Exception as e:
            messagebox.showerror("Lỗi Truy vấn", f"Lỗi khi thực thi truy vấn: {e}")
        con.close()
        clear_input_luong()

    def clear_input_luong():
        manv_entryluong.delete(0,tk.END)
        thang_entryluong.delete(0,tk.END)
        tonggio_entryluong.delete(0,tk.END)
        tongtang_entryluong.delete(0,tk.END)
        tongluong_entryluong.delete(0,tk.END)
        phucap_entryluong.delete(0,tk.END)
        khautru_entryluong.delete(0,tk.END)
        thucnhan_entryluong.delete(0,tk.END)
        timluong_entryluong.delete(0,tk.END)

    def tim_luong():
        tim = cmbTimLuong.get()
        if (tim == 'Mã nhân viên'):
            manv = timluong_entryluong.get()
            load_data_timluong("SELECT * FROM LUONG WHERE MANV='"+manv+"'")
        elif (tim == 'Tháng/Năm'):
            thang = timluong_entryluong.get()
            load_data_timluong("SELECT * FROM LUONG WHERE THANG='"+thang+"'")
        else:
            messagebox.showwarning("thông báo","vui lòng chọn đúng danh mục tìm kiếm")
            return
        
    def load_data_timluong(string):
        for i in treeluong.get_children():
            treeluong.delete(i)
        con = connect_db()
        if con is None: return
        cur = con.cursor()
        try:
            cur.execute(string)
            for row in cur:
                data_list = list(row)
                for i, item in enumerate(data_list):
                    if isinstance(item, datetime.date):
                        data_list[i] = item.strftime('%Y-%m-%d')
                treeluong.insert('', tk.END, values=data_list)
        except Exception as e:
            messagebox.showerror("Lỗi Truy vấn", f"Lỗi khi thực thi truy vấn: {e}")
        con.close()     
        
    def tong_ket_luong():
        
            con = connect_db()
            cur = con.cursor()
            try:
                #tổng kết tổng giờ làm, tính lương, phụ cấp, khấu trừ và thực nhận từ công ngày cho tất cả các tháng và tất cả dữ liệu công ngày
                cur.execute("""WITH BangTongGio AS (
                    SELECT 
                        MANV, 
                        FORMAT(NGAYLAM, 'MM/yyyy') AS THANG, 
                        SUM(GIOCHINH) AS TONGGIOCHINH, 
                        SUM(TANGCA) AS TONGTANGCA
                    FROM CONG_NGAY 
                    GROUP BY MANV, FORMAT(NGAYLAM, 'MM/yyyy')
                )
                    INSERT INTO LUONG (MANV,THANG,TONGGIOCHINH,TONGTANGCA,TONGLUONG,PHUCAP,KHAUTRU,THUCNHAN) 
                        
                SELECT 
                    T.MANV, 
                    T.THANG, 
                    T.TONGGIOCHINH, 
                    T.TONGTANGCA,
                    
                    (T.TONGGIOCHINH * HD.LUONGCB + T.TONGTANGCA * 1.5 * HD.LUONGCB) AS TONGLUONG,
                    
                    (CASE WHEN NV.THAMNIEN < 1 THEN 0 ELSE NV.THAMNIEN * 100000 END) +
                    (CASE WHEN NV.GIOITINH = N'Nữ' THEN 200000 ELSE 0 END) +
                    (CASE WHEN T.TONGGIOCHINH >= 160 THEN 200000 ELSE 0 END) +
                    (CASE WHEN (T.TONGGIOCHINH - 160) >= 20 THEN (T.TONGGIOCHINH - 160) * 1.5 * HD.LUONGCB ELSE 0 END) 
                    AS PHUCAP,
                    ((T.TONGGIOCHINH * HD.LUONGCB + T.TONGTANGCA * 1.5 * HD.LUONGCB) * 0.13 + 50000) AS KHAUTRU,

                    (
                        (T.TONGGIOCHINH * HD.LUONGCB + T.TONGTANGCA * 1.5 * HD.LUONGCB) + 
                        ((CASE WHEN NV.THAMNIEN < 1 THEN 0 ELSE NV.THAMNIEN * 100000 END) +
                        (CASE WHEN NV.GIOITINH = N'Nữ' THEN 200000 ELSE 0 END) +
                        (CASE WHEN T.TONGGIOCHINH >= 160 THEN 200000 ELSE 0 END) +
                        (CASE WHEN (T.TONGGIOCHINH - 160) >= 20 THEN (T.TONGGIOCHINH - 160) * 1.5 * HD.LUONGCB ELSE 0 END))
                    ) - ((T.TONGGIOCHINH * HD.LUONGCB + T.TONGTANGCA * 1.5 * HD.LUONGCB) * 0.13 + 50000) AS THUCNHAN

                FROM BangTongGio T
                JOIN NHANVIEN NV ON T.MANV = NV.MANV
                JOIN HOPDONG HD ON T.MANV = HD.MANV AND HD.NGAY_HET_HAN >= ?
                WHERE NOT EXISTS (
                    SELECT 1 FROM LUONG L 
                    WHERE L.MANV = T.MANV AND L.THANG = T.THANG
                )""",(date.today(),))
                
                con.commit()
                messagebox.showinfo("Thành công", "Tổng kết lương thành công")
            except Exception as e:
                messagebox.showerror("Lỗi", str(e))
            con.close()
            load_data_luong()
            #sau khi tổng kết lương thì đồng thời tổng kết chi tiết lương
            tongket_luong()
            load_data_ct()

    def xoa_luong():
        selected = treeluong.selection() 
        if not selected: 
            messagebox.showwarning("Chưa chọn", "Hãy chọn nhân viên để xóa")
            return
        manv = treeluong.item(selected)["values"][0]
        thang = treeluong.item(selected)["values"][1]
        con = connect_db()
        cur = con.cursor()
        #nếu xóa lương thì đồng thời xóa chi tiết lương
        cur.execute("DELETE FROM LUONG WHERE MANV=? AND THANG = ?", (manv,thang))
        cur.execute("DELETE FROM CHITIETLUONG WHERE MANV = ? AND THANG = ?",(manv,thang))
        con.commit()
        con.close()
        load_data_luong()
        load_data_ct()

    #tạo nút
    FrameButtonLuong = ttk.Frame(FrametabLuong)
    btnTongKetLuong = tk.Button(FrameButtonLuong,text = 'Tổng kết lương',font = ('Times New Roman',15),cursor='hand2',command = tong_ket_luong)
    btnTongKetLuong.pack(side=tk.LEFT)
    ttk.Label(FrameButtonLuong,width=5).pack(side=tk.LEFT)
    btnXoaLuong = tk.Button(FrameButtonLuong,text = 'Xóa',font = ('Times New Roman',15),cursor='hand2',command = xoa_luong)
    btnXoaLuong.pack(side=tk.LEFT)
    ttk.Label(FrameButtonLuong,width=5).pack(side=tk.LEFT)
    btnHuyLuong = tk.Button(FrameButtonLuong,text = 'Hủy',font = ('Times New Roman',15),cursor='hand2',command = clear_input_luong)
    btnHuyLuong.pack(side=tk.LEFT)
    ttk.Label(FrameButtonLuong,width=5).pack(side=tk.LEFT)
    cmbTimLuong = ttk.Combobox(FrameButtonLuong,font = cmb_font,width=15)
    cmbTimLuong['values']=('Mã nhân viên','Tháng/Năm')
    cmbTimLuong.current(0)
    cmbTimLuong.pack(side=tk.LEFT)
    ttk.Label(FrameButtonLuong,width=5).pack(side=tk.LEFT)
    timluong_entryluong = ttk.Entry(FrameButtonLuong,font = (15),width=15)
    timluong_entryluong.pack(side=tk.LEFT)
    btnTimLuong = tk.Button(FrameButtonLuong,text = 'Tìm',font = ('Times New Roman',15),cursor='hand2',command = tim_luong)
    btnTimLuong.pack(side=tk.LEFT)
    ttk.Label(FrameButtonLuong,width=5).pack(side=tk.LEFT)
    btnTatCaLuong = tk.Button(FrameButtonLuong,text = 'Tất cả',font = ('Times New Roman',15),cursor='hand2',command = load_data_luong)
    btnTatCaLuong.pack(side=tk.LEFT)
    ttk.Label(FrameButtonLuong,width=5).pack(side=tk.LEFT)
    btnThoatLuong = tk.Button(FrameButtonLuong,text = 'Thoát',font = ('Times New Roman',15),cursor='hand2',command = thoat_ht)
    btnThoatLuong.pack(side=tk.LEFT)
    ttk.Label(FrameButtonLuong,width=5).pack(side=tk.LEFT)
    
    FrameButtonLuong.grid(row=3,column=0,columnspan=7)

    ttk.Label(FrametabLuong,font = (10)).grid(row=4,column=0)

    ttk.Label(FrametabLuong,text = 'Danh sách:',font = ('Times New Roman',15)).grid(row=5,column=0,columnspan=7)

    ttk.Label(FrametabLuong,font = (10)).grid(row=6,column=0)

    #tạo danh sách chấm công ngày bằng treeview
    columns = ("Mã nhân viên","Tháng/Năm","Tổng giờ chính","Tổng giờ tăng ca","Tổng lương","Phụ cấp","Khấu trừ","Thực nhận")
    treeluong = ttk.Treeview(FrametabLuong,columns = columns,show = "headings",height = 10)

    for col in columns:
        treeluong.heading(col,text = col.capitalize())

    treeluong.column("Mã nhân viên",width = 60,anchor = "center")
    treeluong.column("Tháng/Năm",width=80,anchor="center")
    treeluong.column("Tổng giờ chính",width=120,anchor="center")
    treeluong.column("Tổng giờ tăng ca",width=120,anchor="center")
    treeluong.column("Tổng lương",width=100,anchor="center")
    treeluong.column("Phụ cấp",width=100,anchor="center")
    treeluong.column("Khấu trừ",width=100,anchor="center")
    treeluong.column("Thực nhận",width=100,anchor="center")
    treeluong.grid(row=7,column=0,columnspan=7)

    load_data_luong()
    def select_item_luong(event):
        selected_item = treeluong.focus()
        if selected_item:
            values = treeluong.item(selected_item, 'values')
            if values:
                clear_input_luong()
                manv_entryluong.insert(0, values[0])    
                thang_entryluong.insert(0, values[1])       
                tonggio_entryluong.insert(0,values[2])
                tongtang_entryluong.insert(0,values[3])
                tongluong_entryluong.insert(0,f"{float(values[4]):,.0f}VND")
                phucap_entryluong.insert(0,f"{float(values[5]):,.0f}VND")
                khautru_entryluong.insert(0,f"{float(values[6]):,.0f}VND")
                thucnhan_entryluong.insert(0,f"{float(values[7]):,.0f}VND")
    FrametabLuong.place(x=30,y=20)
    treeluong.bind('<<TreeviewSelect>>', select_item_luong)

    #=================================================================================Chi tiết lương
    tabCT = ttk.Frame(tab_control)
    tab_control.add(tabCT,text = "CHI TIẾT LƯƠNG")
    FrametabCt = tk.Frame(tabCT)
    ttk.Label(FrametabCt,text = "QUẢN LÝ LƯƠNG",font = ('Times New Roman',20,'bold')).grid(row=0,column=0,columnspan=11)

    ttk.Label(FrametabCt,font = (10)).grid(row=1,column=0,columnspan=11)

    lblFrame1 = ttk.Frame(FrametabCt)
    ttk.Label(lblFrame1,text = 'Mã nhân viên: ',font = ('Times New Roman',15)).pack(side=tk.TOP)
    ttk.Label(lblFrame1,font = (10)).pack(side=tk.TOP)
    ttk.Label(lblFrame1,text = 'Tháng/Năm: ',font = ('Times New Roman',15)).pack(side=tk.TOP)
    ttk.Label(lblFrame1,font = (10)).pack(side=tk.TOP)
    ttk.Label(lblFrame1,text = 'Lương cơ bản: ',font = ('Times New Roman',15)).pack(side=tk.TOP)
    ttk.Label(lblFrame1,font = (10)).pack(side=tk.TOP)
    ttk.Label(lblFrame1,text = 'Lương tăng ca: ',font = ('Times New Roman',15)).pack(side=tk.TOP)
    ttk.Label(lblFrame1,font = (10)).pack(side=tk.TOP)
    ttk.Label(lblFrame1,text = 'Tổng lương: ',font = ('Times New Roman',15)).pack(side=tk.TOP)
    ttk.Label(lblFrame1,font = (10)).pack(side=tk.TOP)
    lblFrame1.grid(row=2,column=0)

    ttk.Label(FrametabCt,width=10).grid(row=2,column=1)

    Frame1 = ttk.Frame(FrametabCt)
    manv_entryct = ttk.Entry(Frame1,font = (15),width=10)
    manv_entryct.pack(side=tk.TOP)
    ttk.Label(Frame1,font = (10)).pack(side=tk.TOP)
    thangnam_entryct = ttk.Entry(Frame1,font = (15),width=10)
    thangnam_entryct.pack(side=tk.TOP)
    ttk.Label(Frame1,font = (10)).pack(side=tk.TOP)
    luongcb_entryct = ttk.Entry(Frame1,font = (15),width=10)
    luongcb_entryct.pack(side=tk.TOP)
    ttk.Label(Frame1,font = (10)).pack(side=tk.TOP)
    luongtc_entryct = ttk.Entry(Frame1,font = (15),width=10)
    luongtc_entryct.pack(side=tk.TOP)
    ttk.Label(Frame1,font = (10)).pack(side=tk.TOP)
    tongluong_entryct = ttk.Entry(Frame1,font = (15),width=10)
    tongluong_entryct.pack(side=tk.TOP)
    ttk.Label(Frame1,font = (10)).pack(side=tk.TOP)
    Frame1.grid(row=2,column=2)

    ttk.Label(FrametabCt,width=10).grid(row=2,column=3)

    lblFrame2 = ttk.Frame(FrametabCt)
    ttk.Label(lblFrame2,text = "Thâm niên: ",font=('Times New Roman',15)).pack(side=tk.TOP)
    ttk.Label(lblFrame2,font = (10)).pack(side=tk.TOP)
    ttk.Label(lblFrame2,text = "Phụ nữ: ",font = ('Times New Roman',15)).pack(side=tk.TOP)
    ttk.Label(lblFrame2,font = (10)).pack(side=tk.TOP)
    ttk.Label(lblFrame2,text = "Chuyên cần: ",font = ('Times New Roman',15)).pack(side=tk.TOP)
    ttk.Label(lblFrame2,font = (10)).pack(side=tk.TOP)
    ttk.Label(lblFrame2,text = "Khen thưởng: ",font = ('Times New Roman',15)).pack(side=tk.TOP)
    ttk.Label(lblFrame2,font = (10)).pack(side=tk.TOP)
    ttk.Label(lblFrame2,text = "Tổng khấu trừ: ",font = ('Times New Roman',15)).pack(side=tk.TOP)
    ttk.Label(lblFrame2,font = (10)).pack(side=tk.TOP)
    lblFrame2.grid(row=2,column=4)

    ttk.Label(FrametabCt,width=10).grid(row=2,column=5)

    Frame2 = ttk.Frame(FrametabCt)
    thamnien_entryct = ttk.Entry(Frame2,font = (15),width=10)
    thamnien_entryct.pack(side=tk.TOP)
    ttk.Label(Frame2,font=(10)).pack(side=tk.TOP)
    phunu_entryct = ttk.Entry(Frame2,font = (15),width=10)
    phunu_entryct.pack(side=tk.TOP)
    ttk.Label(Frame2,font=(10)).pack(side=tk.TOP)
    chuyencan_entryct = ttk.Entry(Frame2,font = (15),width=10)
    chuyencan_entryct.pack(side=tk.TOP)
    ttk.Label(Frame2,font=(10)).pack(side=tk.TOP)
    khenthuong_entryct = ttk.Entry(Frame2,font = (15),width=10)
    khenthuong_entryct.pack(side=tk.TOP)
    ttk.Label(Frame2,font=(10)).pack(side=tk.TOP)
    tongkhautru_entryct = ttk.Entry(Frame2,font = (15),width=10)
    tongkhautru_entryct.pack(side=tk.TOP)
    ttk.Label(Frame2,font=(10)).pack(side=tk.TOP)
    Frame2.grid(row=2,column=6)

    ttk.Label(FrametabCt,font = (10)).grid(row=2,column=7)

    lblFrame3 = ttk.Frame(FrametabCt)
    ttk.Label(lblFrame3,text = "Thuế: ",font=('Times New Roman',15)).pack(side=tk.TOP)
    ttk.Label(lblFrame3,font = (10)).pack(side=tk.TOP)
    ttk.Label(lblFrame3,text = "BHYT: ",font = ('Times New Roman',15)).pack(side=tk.TOP)
    ttk.Label(lblFrame3,font = (10)).pack(side=tk.TOP)
    ttk.Label(lblFrame3,text = "BHXH: ",font = ('Times New Roman',15)).pack(side=tk.TOP)
    ttk.Label(lblFrame3,font = (10)).pack(side=tk.TOP)
    ttk.Label(lblFrame3,text = "BHTN: ",font = ('Times New Roman',15)).pack(side=tk.TOP)
    ttk.Label(lblFrame3,font = (10)).pack(side=tk.TOP)
    ttk.Label(lblFrame3,text = "Công đoàn: ",font = ('Times New Roman',15)).pack(side=tk.TOP)
    ttk.Label(lblFrame3,font = (10)).pack(side=tk.TOP)
    ttk.Label(lblFrame3,text = "Khác (Phạt): ",font = ('Times New Roman',15)).pack(side=tk.TOP)
    ttk.Label(lblFrame3,font = (10)).pack(side=tk.TOP)
    lblFrame3.grid(row=2,column=8)

    ttk.Label(FrametabCt,font = (10)).grid(row=2,column=9)

    Frame3 = ttk.Frame(FrametabCt)
    thue_entryct = ttk.Entry(Frame3,font = (15),width=10)
    thue_entryct.pack(side=tk.TOP)
    ttk.Label(Frame3,font=(10)).pack(side=tk.TOP)
    bhyt_entryct = ttk.Entry(Frame3,font = (15),width=10)
    bhyt_entryct.pack(side=tk.TOP)
    
    ttk.Label(Frame3,font=(10)).pack(side=tk.TOP)
    bhxh_entryct = ttk.Entry(Frame3,font = (15),width=10)
    bhxh_entryct.pack(side=tk.TOP)

    ttk.Label(Frame3,font=(10)).pack(side=tk.TOP)
    bhtn_entryct = ttk.Entry(Frame3,font = (15),width=10)
    bhtn_entryct.pack(side=tk.TOP)
    ttk.Label(Frame3,font=(10)).pack(side=tk.TOP)
    congdoan_entryct = ttk.Entry(Frame3,font = (15),width=10)
    congdoan_entryct.pack(side=tk.TOP)
    ttk.Label(Frame3,font=(10)).pack(side=tk.TOP)
    khac_entryct = ttk.Entry(Frame3,font = (15),width=10)
    khac_entryct.pack(side=tk.TOP)
    ttk.Label(Frame3,font=(10)).pack(side=tk.TOP)   
    Frame3.grid(row=2,column=10)

    ttk.Label(FrametabCt,font = (10)).grid(row=3,column=0)

    def clear_input_ct():
        manv_entryct.delete(0,tk.END)
        thangnam_entryct.delete(0,tk.END)
        luongcb_entryct.delete(0,tk.END)
        luongtc_entryct.delete(0,tk.END)
        tongluong_entryct.delete(0,tk.END)
        thamnien_entryct.delete(0,tk.END)
        phunu_entryct.delete(0,tk.END)
        chuyencan_entryct.delete(0,tk.END)
        khenthuong_entryct.delete(0,tk.END)
        tongkhautru_entryct.delete(0,tk.END)
        thue_entryct.delete(0,tk.END)
        bhyt_entryct.delete(0,tk.END)
        bhxh_entryct.delete(0,tk.END)
        bhtn_entryct.delete(0,tk.END)
        congdoan_entryct.delete(0,tk.END)
        khac_entryct.delete(0,tk.END)
        timct_entryct.delete(0,tk.END)

    def sua_ct():
        selected = treect.selection() 
        if not selected: 
            messagebox.showwarning("Chưa chọn", "Hãy chọn nhân viên để sửa") 
            return 
        tb = messagebox.askokcancel("Xác nhận","bạn có chắc chắn muốn sửa không? (không sửa được mã nhân viên, lương, tháng/năm và khấu trừ)")
        if tb>0:
            luu_ct()

    def luu_ct():
        manv = manv_entryct.get()
        thuong = khenthuong_entryct.get()
        congdoan = congdoan_entryct.get()
        khac = khac_entryct.get()
        thang = thangnam_entryct.get()
        con = connect_db()
        cur = con.cursor()
        #sửa các chi tiết lương như: thưởng, phạt, chi phí công đoàn (vì các chi tiết khác đã tính theo % so với tổng lương)
        cur.execute("""UPDATE CHITIETLUONG SET PC_THUONG = ?,KT_CONGDOAN = ?,KT_KHAC = ? WHERE MANV = ? AND THANG = ?""",\
                     (thuong,congdoan,khac,manv,thang)) 
        cur.execute("""UPDATE LUONG SET PHUCAP = CT.PC_THAMNIEN + CT.PC_PHUNU + CT.PC_CHUYENCAN + CT.PC_THUONG, 
                    KHAUTRU = CT.KT_THUE + CT.KT_BHYT + CT.KT_BHXH + CT.KT_BHTN + CT.KT_CONGDOAN + CT.KT_KHAC,
                    THUCNHAN = L.TONGLUONG + (CT.PC_THAMNIEN + CT.PC_PHUNU + CT.PC_CHUYENCAN + CT.PC_THUONG) 
                                - (CT.KT_THUE + CT.KT_BHYT + CT.KT_BHXH + CT.KT_BHTN + CT.KT_CONGDOAN + CT.KT_KHAC)
                    FROM LUONG L JOIN CHITIETLUONG CT ON L.MANV = CT.MANV WHERE L.MANV = ? AND L.THANG = ?""",(manv,thang))
        con.commit()
        con.close() 
        load_data_ct()
        load_data_luong()

    def load_data_ct():
        for i in treect.get_children():
            treect.delete(i)
        con = connect_db()
        if con is None: return
        cur = con.cursor()
        try:
            cur.execute('SELECT * FROM CHITIETLUONG')
            for row in cur:
                data_list = list(row)
                for i, item in enumerate(data_list):
                    if isinstance(item, datetime.date):
                        data_list[i] = item.strftime('%Y-%m-%d')
                treect.insert('', tk.END, values=data_list)
        except Exception as e:
            messagebox.showerror("Lỗi Truy vấn", f"Lỗi khi thực thi truy vấn: {e}")
        con.close()
        clear_input_ct()

    def tim_ct():
        tim = cmbTimCT.get()
        if (tim == 'Mã nhân viên'):
            manv = timct_entryct.get()
            load_data_timct("SELECT * FROM CHITIETLUONG WHERE MANV='"+manv+"'")
        elif (tim == 'Tháng/Năm'):
            thangnam = timct_entryct.get()
            load_data_timct("SELECT * FROM CHITIETLUONG WHERE THANG='"+thangnam+"'")
        else:
            messagebox.showwarning("thông báo","vui lòng chọn đúng danh mục tìm kiếm")
            return
        
    def load_data_timct(string):
        for i in treect.get_children():
            treect.delete(i)
        con = connect_db()
        if con is None: return
        cur = con.cursor()
        try:
            cur.execute(string)
            for row in cur:
                data_list = list(row)
                for i, item in enumerate(data_list):
                    if isinstance(item, datetime.date):
                        data_list[i] = item.strftime('%Y-%m-%d')
                treect.insert('', tk.END, values=data_list)
        except Exception as e:
            messagebox.showerror("Lỗi Truy vấn", f"Lỗi khi thực thi truy vấn: {e}")
        con.close()

    def tongket_luong():
        tb = messagebox.askokcancel("Xác nhận","bạn có chắc chắn muốn tổng kết lương không?")
        if tb>0:
            con = connect_db()
            cur = con.cursor()
            #chi tiết lương được tổng kết từ công ngày
            cur.execute("""INSERT INTO CHITIETLUONG 
                        (MANV,THANG,LUONGCHINH,LUONGTANGCA,PC_THAMNIEN,PC_PHUNU,PC_CHUYENCAN,PC_THUONG,
                        KT_THUE,KT_BHYT,KT_BHXH,KT_BHTN,KT_CONGDOAN,KT_KHAC)
                SELECT L.MANV,L.THANG,
                (L.TONGGIOCHINH * HD.LUONGCB) AS LUONGCHINH,
                (L.TONGTANGCA * HD.LUONGCB * 1.5) AS LUONGTANGCA,
                
                (CASE WHEN NV.THAMNIEN < 1 THEN 0 ELSE NV.THAMNIEN * 100000 END) AS PC_THAMNIEN,
                
                (CASE WHEN NV.GIOITINH = N'Nữ' THEN 200000 ELSE 0 END) AS PC_PHUNU,
                
                (CASE WHEN L.TONGGIOCHINH >= 160 THEN 200000 ELSE 0 END) AS PC_CHUYENCAN,
                
                (CASE WHEN (L.TONGGIOCHINH - 160) >= 20 THEN (L.TONGGIOCHINH - 160) * 1.5 * HD.LUONGCB ELSE 0 END) AS PC_THUONG,
                
                (CASE WHEN L.TONGLUONG > 9000000 THEN L.TONGLUONG * 0.1 ELSE 0 END) AS KT_THUE,
                
                (L.TONGLUONG * 0.015) AS KT_BHYT,
                (L.TONGLUONG * 0.105) AS KT_BHXH,
                (L.TONGLUONG * 0.01) AS KT_BHTN,
                50000 AS KT_CONGDOAN,
                0 AS KT_KHAC

            FROM LUONG L
            JOIN HOPDONG HD ON L.MANV = HD.MANV AND HD.NGAY_HET_HAN >= ?
            JOIN NHANVIEN NV ON L.MANV = NV.MANV
            
            WHERE NOT EXISTS (
                SELECT 1 FROM CHITIETLUONG CTL 
                WHERE CTL.MANV = L.MANV AND CTL.THANG = L.THANG
            )""",(date.today(),))
                    
            con.commit()
            con.close() 
    def xuat_excel():
        if len(treect.get_children())<1:
            messagebox.showwarning("thông báo","không có dữ liệu để xuất")
            return 
        
        file_path = filedialog.asksaveasfilename(defaultextension=".xlsx",filetypes=[("Excel files","*.xlsx"),("All files","*.*")],title="Lưu file Excel")
        if not file_path:
            return
        try:
            all_data = []
            for item in treect.get_children():
                row_values = treect.item(item)['values']
                all_data.append(row_values)
            columns_name = ["Mã nhân viên","Tháng/Năm","Lương cơ bản","Lương tăng ca","Thâm niên","Phụ nữ","Chuyên cần","Khen thưởng",\
               "Thuế","BHYT","BHXH","BHTN","Công đoàn","Khác"]
            df = pd.DataFrame(all_data,columns = columns_name)
            df.to_excel(file_path,index = False)
            messagebox.showinfo("Thành công",f"Đã xuất file Excel tại:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Lỗi Xuất file",f"Có lỗi xảy ra:\n{e}")
   
    #tạo nút
    FrameButtonCT = ttk.Frame(FrametabCt)
    btnSuaCT=tk.Button(FrameButtonCT,text = 'Sửa',font=('Times New Roman',15),cursor = 'hand2',command = sua_ct)
    btnSuaCT.pack(side=tk.LEFT)
    ttk.Label(FrameButtonCT,width=5).pack(side=tk.LEFT)
    btnHuyCT=tk.Button(FrameButtonCT,text = 'Hủy',font=('Times New Roman',15),cursor = 'hand2',command = clear_input_ct)
    btnHuyCT.pack(side=tk.LEFT)
    ttk.Label(FrameButtonCT,width=5).pack(side=tk.LEFT)
    cmbTimCT = ttk.Combobox(FrameButtonCT,font = cmb_font,width=15)
    cmbTimCT['values']=('Mã nhân viên','Tháng/Năm')
    cmbTimCT.current(0)
    cmbTimCT.pack(side=tk.LEFT)
    ttk.Label(FrameButtonCT,width=5).pack(side=tk.LEFT)
    timct_entryct = ttk.Entry(FrameButtonCT,font = (15),width=15)
    timct_entryct.pack(side=tk.LEFT)
    btnTimCT = tk.Button(FrameButtonCT,text = 'Tìm',font = ('Times New Roman',15),cursor = 'hand2',command = tim_ct)
    btnTimCT.pack(side=tk.LEFT)
    ttk.Label(FrameButtonCT,width=5).pack(side=tk.LEFT)
    btnTatCaCT = tk.Button(FrameButtonCT,text = 'Tất cả',font = ('Times New Roman',15),cursor = 'hand2',command = load_data_ct)
    btnTatCaCT.pack(side=tk.LEFT)
    ttk.Label(FrameButtonCT,width=5).pack(side=tk.LEFT)
    btnExcelCT = tk.Button(FrameButtonCT,text = 'Xuất Excel',font = ('Times New Roman',15),cursor = 'hand2',command = xuat_excel)
    btnExcelCT.pack(side=tk.LEFT)
    ttk.Label(FrameButtonCT,width=5).pack(side=tk.LEFT)
    btnThoatCT = tk.Button(FrameButtonCT,text = 'Thoát',font = ('Times New Roman',15),cursor = 'hand2',command = thoat_ht)
    btnThoatCT.pack(side=tk.LEFT)
    FrameButtonCT.grid(row=3,column=0,columnspan=11)
    ttk.Label(FrametabCt,font = (10)).grid(row=4,column=0)
    ttk.Label(FrametabCt,text = 'Danh sách chi tiết lương:',font = ('Times New Roman',15)).grid(row=5,column=0,columnspan=11)
    ttk.Label(FrametabCt,font = (10)).grid(row=6,column=0)
    columns = ("Mã nhân viên","Tháng/Năm","Lương cơ bản","Lương tăng ca","Thâm niên","Phụ nữ","Chuyên cần","Khen thưởng",\
               "Thuế","BHYT","BHXH","BHTN","Công đoàn","Khác")
    treect = ttk.Treeview(FrametabCt,columns = columns,show = "headings",height = 10)

    for col in columns:
        treect.heading(col,text = col.capitalize())

    treect.column("Mã nhân viên",width = 60,anchor = "center")
    treect.column("Tháng/Năm",width=60,anchor="center")   
    treect.column("Lương cơ bản",width=100,anchor="center")
    treect.column("Lương tăng ca",width=100,anchor="center")
    treect.column("Thâm niên",width=60,anchor="center")
    treect.column("Phụ nữ",width=60,anchor="center")
    treect.column("Chuyên cần",width=60,anchor="center")
    treect.column("Khen thưởng",width=100,anchor="center")
    treect.column("Thuế",width=60,anchor="center")
    treect.column("BHYT",width=60,anchor="center")
    treect.column("BHXH",width=60,anchor="center")
    treect.column("BHTN",width=60,anchor="center")
    treect.column("Công đoàn",width=60,anchor="center")
    treect.column("Khác",width=60,anchor="center")
    treect.grid(row=7,column=0,columnspan=11)
    load_data_ct()

    def select_item_ct(event):
        selected_item = treect.focus()
        if selected_item:
            values = treect.item(selected_item, 'values')
            if values:
                clear_input_ct()
                manv_entryct.insert(0, values[0])    
                thangnam_entryct.insert(0, values[1])  
                luongcb_entryct.insert(0, f"{float(values[2]):,.0f}VND")     
                luongtc_entryct.insert(0,f"{float(values[3]):,.0f}VND")
                tongluong_entryct.insert(0,f"{float(values[2])+float(values[3]):,.0f}VND")
                thamnien_entryct.insert(0,f"{float(values[4]):,.0f}VND")
                phunu_entryct.insert(0,f"{float(values[5]):,.0f}VND")
                chuyencan_entryct.insert(0,f"{float(values[6]):,.0f}VND")
                khenthuong_entryct.insert(0,f"{float(values[7]):,.0f}VND")
                tongkhautru_entryct.insert(0,f"{float(values[8])+float(values[9])+float(values[10])+\
                                                float(values[11])+float(values[12])+float(values[13]):,.0f}VND")
                thue_entryct.insert(0,f"{float(values[8]):,.0f}VND")
                bhyt_entryct.insert(0,f"{float(values[9]):,.0f}VND")
                bhxh_entryct.insert(0,f"{float(values[10]):,.0f}VND")
                bhtn_entryct.insert(0,f"{float(values[11]):,.0f}VND")
                congdoan_entryct.insert(0,f"{float(values[12]):,.0f}VND")
                khac_entryct.insert(0,f"{float(values[13]):,.0f}VND")
    FrametabCt.place(x=55,y=15)
    treect.bind('<<TreeviewSelect>>', select_item_ct)

    #=================================================================================Tài khoản
    tabTaiKhoan = ttk.Frame(tab_control)
    tab_control.add(tabTaiKhoan,text = "TÀI KHOẢN")
    frameTaiKhoan = ttk.Frame(tabTaiKhoan)
    ttk.Label(frameTaiKhoan,text = "QUẢN LÝ TÀI KHOẢN",font = ('Times New Roman',20,'bold')).grid(row=0,column=0,columnspan=2)

    ttk.Label(frameTaiKhoan,font = (10)).grid(row=1,column=0,columnspan=2)

    FrameUN = ttk.Frame(frameTaiKhoan)
    ttk.Label(FrameUN,text = "Tên đăng nhập: ",font = ('Times New Roman',15)).pack(side=tk.LEFT)
    username_entry = ttk.Entry(FrameUN,font = (15),width=20)
    username_entry.pack(side=tk.LEFT)
    FrameUN.grid(row=2,column=0)

    FrameP = ttk.Frame(frameTaiKhoan)
    ttk.Label(FrameP,text = "Mật khẩu: ",font = ('Times New Roman',15)).pack(side=tk.LEFT)
    password_entry = ttk.Entry(FrameP,font = (15),width=20,show="*")
    password_entry.pack(side=tk.LEFT)
    FrameP.grid(row=2,column=1)

    ttk.Label(frameTaiKhoan,font = (10)).grid(row=3,column=0,columnspan=2)

    def load_data_taikhoan():
        for i in treetk.get_children():
            treetk.delete(i)
        con = connect_db()
        if con is None: return
        cur = con.cursor()
        try:
            #chỉ hiển thị tên tài khoản đã tạo hoặc đăng nhập vào hệ thống
            cur.execute('SELECT TENTAIKHOAN FROM TAIKHOAN')
            for row in cur:
                data_list = list(row)
                for i, item in enumerate(data_list):
                    if isinstance(item, datetime.date):
                        data_list[i] = item.strftime('%Y-%m-%d')
                treetk.insert('', tk.END, values=data_list)
        except Exception as e:
            messagebox.showerror("Lỗi Truy vấn", f"Lỗi khi thực thi truy vấn: {e}")
        con.close()
        clear_input_taikhoan()

    def reset_password():
        username = username_entry.get()
        password = '123456'
        con = connect_db()
        cur = con.cursor()
        #đặt lại mật khẩu cho tài khoản được chọn là '123456'
        cur.execute("UPDATE TAIKHOAN SET PASS = ? WHERE TENTAIKHOAN = ?", (password, username))
        con.commit()
        con.close()
        messagebox.showinfo("Thành công", "Đặt lại mật khẩu thành công")
        load_data_taikhoan()

    def delete_taikhoan():
        selected = treetk.selection() 
        if not selected: 
            messagebox.showwarning("Chưa chọn", "Hãy chọn nhân viên để sửa") 
            return 
        username = treetk.item(selected)["values"][0]
        tb = messagebox.askokcancel("Xác nhận","bạn có chắc chắn muốn xóa tài khoản này không?")
        if tb>0:
            con = connect_db()
            cur = con.cursor()

            #không cho phép xóa tài khoản đang được đăng nhập vào hệ thống (xóa tài khoản của chính nhân viên đang thao tác)
            if username == tai_khoan_hien_tai:
                messagebox.showwarning("thông báo","không thể xóa tài khoản đang đăng nhập hệ thống")
                return
            #nếu mã nhân viên đó giữ chức vụ giám đốc thì không được xóa trực tiếp
            cur.execute("SELECT COUNT(*) FROM NHANVIEN WHERE MANV = ? AND CHUCVU = N'Giám đốc'", (username,))
            if cur.fetchone()[0] !=0:
                messagebox.showwarning("Lỗi","Không thể xóa tài khoản của giám đốc")
                return
            
            cur.execute("DELETE FROM TAIKHOAN WHERE TENTAIKHOAN = ?", (username,))
            con.commit()
            con.close()
            messagebox.showinfo("Thành công", "Xóa tài khoản thành công")
            load_data_taikhoan()

    def clear_input_taikhoan():
        username_entry.delete(0,tk.END)
        password_entry.delete(0,tk.END)

    
    FrameButtonTK = ttk.Frame(frameTaiKhoan)
    btnDatLai = tk.Button(FrameButtonTK,text = 'Đặt lại mật khẩu',font = ('Times New Roman',15),cursor='hand2',command = reset_password)
    btnDatLai.pack(side=tk.LEFT)
    ttk.Label(FrameButtonTK,width=5).pack(side=tk.LEFT)
    btnHuy = tk.Button(FrameButtonTK,text = 'Hủy',font = ('Times New Roman',15),cursor='hand2',command = clear_input_taikhoan)
    btnHuy.pack(side=tk.LEFT)
    ttk.Label(FrameButtonTK,width=5).pack(side=tk.LEFT)
    btnXoaTK = tk.Button(FrameButtonTK,text = 'Xóa tài khoản',font = ('Times New Roman',15),cursor='hand2',command = delete_taikhoan)
    btnXoaTK.pack(side=tk.LEFT)
    ttk.Label(FrameButtonTK,width=5).pack(side=tk.LEFT)
    btnTatcaTK = tk.Button(FrameButtonTK,text = 'Tất cả',font = ('Times New Roman',15),cursor='hand2',command = load_data_taikhoan)
    btnTatcaTK.pack(side=tk.LEFT)
    ttk.Label(FrameButtonTK,width=5).pack(side=tk.LEFT)
    btnThoatTK = tk.Button(FrameButtonTK,text = 'Thoát',font = ('Times New Roman',15),cursor='hand2',command = thoat_ht)
    btnThoatTK.pack(side=tk.LEFT)
    FrameButtonTK.grid(row=4,column=0,columnspan=2)

    ttk.Label(frameTaiKhoan,font = (10)).grid(row=5,column=0,columnspan=2)

    ttk.Label(frameTaiKhoan,text = 'Danh sách tài khoản:',font = ('Times New Roman',15)).grid(row=6,column=0,columnspan=2)

    ttk.Label(frameTaiKhoan,font = (10)).grid(row=7,column=0,columnspan=2)
    columns = ("Tên đăng nhập",)
    treetk = ttk.Treeview(frameTaiKhoan,columns = columns,show = "headings",height = 10)

    for col in columns:
        treetk.heading(col,text = col.capitalize())

    treetk.column("Tên đăng nhập",width = 150,anchor = "center")
    treetk.grid(row=8,column=0,columnspan=2)

    ttk.Label(frameTaiKhoan,font = (10)).grid(row=9,column=0,columnspan=2)

    ttk.Label(frameTaiKhoan,text = 'Mật khẩu mặc định sau khi đặt lại là: 123456',\
              font = ('Times New Roman',12,'italic')).grid(row=10,column=0,columnspan=2)
    load_data_taikhoan()

    def select_item_tk(event):
        selected_item = treetk.focus()
        if selected_item:
            values = treetk.item(selected_item, 'values')
            if values:
                username_entry.delete(0,tk.END)
                password_entry.delete(0,tk.END)
                username_entry.insert(0, values[0])    
                con = connect_db()
                cur = con.cursor()
                #hiển thị mã nhân viên dạng *
                mk = ""
                for char in cur.execute("SELECT PASS FROM TAIKHOAN WHERE TENTAIKHOAN = ?",(values[0])).fetchone()[0]:
                    mk = mk + '*'
                password_entry.insert(0,mk)
                con.close()

    frameTaiKhoan.place(x = 200,y=80)
    treetk.bind('<<TreeviewSelect>>', select_item_tk)

root.mainloop()
