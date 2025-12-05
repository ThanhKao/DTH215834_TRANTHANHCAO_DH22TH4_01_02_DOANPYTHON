CREATE DATABASE QLCHXM
GO

USE QLCHXM
GO

-- 1. Bảng Nhân Viên (Giữ nguyên)
CREATE TABLE NhanVien (
    MaNhanVien NVARCHAR(10) NOT NULL PRIMARY KEY,
    HoVaTen NVARCHAR(100) NOT NULL,
    SoDienThoai VARCHAR(15),
    DiaChi NVARCHAR(255),
    TrangThai INT DEFAULT 1 NOT NULL -- 1: Đang làm, 0: Nghỉ việc
);
GO

-- 2. Bảng Xe Máy
CREATE TABLE XeMay (
    SoKhung VARCHAR(17) NOT NULL PRIMARY KEY, 
    LoaiXe NVARCHAR(30),                      
    TenXe NVARCHAR(50),
    HangSanXuat NVARCHAR(50),
    MauSac NVARCHAR(20),
    NamSanXuat INT,
    GiaBan DECIMAL(18, 0)
);
GO

-- 3. Bảng Khách Hàng
CREATE TABLE KhachHang (
    MaKhachHang NVARCHAR(20) NOT NULL PRIMARY KEY, -- Đã sửa: NVARCHAR để nhập tay
    HoTen NVARCHAR(100) NOT NULL,
    SoDienThoai VARCHAR(15),
    DiaChi NVARCHAR(255),
    CCCD VARCHAR(20)
);
GO

-- 4. Bảng hoá đơn
CREATE TABLE HoaDon (
    MaHoaDon NVARCHAR(20) NOT NULL PRIMARY KEY,
    MaNhanVien NVARCHAR(10), 
    MaKhachHang NVARCHAR(20), 
    SoKhung VARCHAR(17), 
    NgayBan DATE DEFAULT GETDATE(),
    TongTien DECIMAL(18, 0),
    GhiChu NVARCHAR(MAX),
    
    FOREIGN KEY (MaNhanVien) REFERENCES NhanVien(MaNhanVien),
    FOREIGN KEY (MaKhachHang) REFERENCES KhachHang(MaKhachHang),
    FOREIGN KEY (SoKhung) REFERENCES XeMay(SoKhung)
);
GO

-- 5. Bảng Tài Khoản (Cập nhật VaiTro: Admin, QuanLy, NhanVien)
CREATE TABLE TaiKhoan (
    TenDangNhap NVARCHAR(50) PRIMARY KEY,
    MatKhau NVARCHAR(255) NOT NULL, -- Sẽ lưu mã hóa SHA-256
    MaNhanVien NVARCHAR(10) NOT NULL,
    -- Vai trò: 'Admin' (Toàn quyền), 'QuanLy' (Quản lý kho/nhân viên), 'NhanVien' (Chỉ bán hàng)
    VaiTro NVARCHAR(20) DEFAULT 'NhanVien' NOT NULL, 
    FOREIGN KEY (MaNhanVien) REFERENCES NhanVien(MaNhanVien)
);
GO


-- 1. Thêm dữ liệu Bảng Nhân Viên (Admin, Quản lý, Nhân viên)
INSERT INTO NhanVien (MaNhanVien, HoVaTen, SoDienThoai, DiaChi, TrangThai) VALUES
('NV01', N'Trần Quản N', '0901000001', N'Hà Nội', 1),
('NV02', N'Trần Thị C', '0901000002', N'Đà Nẵng', 1),
('NV03', N'Lê Ngọc K', '0901000003', N'TP.HCM', 1);
GO

-- 2. Thêm dữ liệu Bảng Xe Máy (Đủ loại: Tay ga, Xe số, Côn tay)
INSERT INTO XeMay (SoKhung, LoaiXe, TenXe, HangSanXuat, MauSac, NamSanXuat, GiaBan) VALUES
('SK1111', N'Xe Tay Ga', N'Honda Vision', 'Honda', N'Trắng', 2024, 36000000),
('SK2222', N'Xe Tay Ga', N'Honda SH 150i', 'Honda', N'Đen mờ', 2023, 110000000),
('SK3333', N'Xe Số', N'Wave Alpha', 'Honda', N'Xanh', 2024, 18500000),
('SK4444', N'Xe Côn Tay', N'Yamaha Exciter 155', 'Yamaha', N'Xanh GP', 2024, 52000000),
('SK5555', N'Xe Côn Tay', N'Winner X', 'Honda', N'Đỏ đen', 2023, 40000000),
('SK6666', N'Xe Tay Ga', N'Air Blade 160', 'Honda', N'Xám', 2024, 56000000),
('SK7777', N'Xe Điện', N'VinFast Klara S', 'VinFast', N'Đỏ', 2023, 35000000),
('SK8888', N'Xe Số', N'Yamaha Sirius', 'Yamaha', N'Đen', 2023, 21000000);
GO

-- 3. Thêm dữ liệu Bảng Khách Hàng (Nhập mã tay KH01, KH02...)
INSERT INTO KhachHang (MaKhachHang, HoTen, SoDienThoai, DiaChi, CCCD) VALUES
('KH01', N'Nguyễn Văn D', '0988111222', N'Quận 1, TP.HCM', '079123456789'),
('KH02', N'Trần Thị F', '0988333444', N'Quận 5, TP.HCM', '079987654321'),
('KH03', N'Lê Văn E', '0988555666', N'Thủ Đức, TP.HCM', '079111222333'),
('KH04', N'Phạm Thị M', '0988777888', N'Bình Thạnh, TP.HCM', '079444555666');
GO

-- 4. Thêm dữ liệu Bảng Hóa Đơn (Giả lập 2 xe đã bán: SK1111 và SK3333)
-- Lưu ý: Mã hóa đơn nhập tay (HD01, HD02...)
INSERT INTO HoaDon (MaHoaDon, MaNhanVien, MaKhachHang, SoKhung, NgayBan, TongTien, GhiChu) VALUES
('HD01', 'NV03', 'KH01', 'SK1111', '2024-01-15', 36000000, N'Khách trả tiền mặt'),
('HD02', 'NV03', 'KH02', 'SK3333', '2024-02-20', 18500000, N'Tặng kèm mũ bảo hiểm');
GO

-- 5. Thêm dữ liệu Bảng Tài Khoản
-- Mật khẩu mặc định là "123" (đã mã hóa SHA-256)
-- Hash SHA256 của "123" là: a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3
INSERT INTO TaiKhoan (TenDangNhap, MatKhau, MaNhanVien, VaiTro) VALUES
('admin', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'NV01', 'Admin'),
('quanly', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'NV02', 'QuanLy'),
('nhanvien', 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3', 'NV03', 'NhanVien');
GO
 select *from NhanVien
 select *from XeMay
 select *from KhachHang
 select *from TaiKhoan
