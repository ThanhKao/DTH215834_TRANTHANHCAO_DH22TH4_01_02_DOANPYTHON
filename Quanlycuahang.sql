CREATE DATABASE QLCHXM
GO

USE QLCHXM
GO


CREATE TABLE NhanVien (
    MaNhanVien NVARCHAR(10) NOT NULL PRIMARY KEY,
    HoVaTen NVARCHAR(100) NOT NULL,
    SoDienThoai VARCHAR(15),
    DiaChi NVARCHAR(255),
    TrangThai INT DEFAULT 1 NOT NULL -- 1: Đang làm, 0: Nghỉ việc
);
GO


CREATE TABLE VatLieu (
    MaVatLieu VARCHAR(17) NOT NULL PRIMARY KEY, 
    LoaiVatLieu NVARCHAR(30),                      
    TenVatLieu NVARCHAR(50),
    HangSanXuat NVARCHAR(50),
    GiaBan DECIMAL(18, 0)
);
GO


CREATE TABLE KhachHang (
    MaKhachHang NVARCHAR(20) NOT NULL PRIMARY KEY, -- Đã sửa: NVARCHAR để nhập tay
    HoTen NVARCHAR(100) NOT NULL,
    SoDienThoai VARCHAR(15),
    DiaChi NVARCHAR(255),
    CCCD VARCHAR(20)
);
GO


CREATE TABLE HoaDon (
    MaHoaDon NVARCHAR(20) NOT NULL PRIMARY KEY,
    MaNhanVien NVARCHAR(10), 
    MaKhachHang NVARCHAR(20), 
    MaVatLieu VARCHAR(17), 
    NgayBan DATE DEFAULT GETDATE(),
    TongTien DECIMAL(18, 0),
    GhiChu NVARCHAR(MAX),
    
    FOREIGN KEY (MaNhanVien) REFERENCES NhanVien(MaNhanVien),
    FOREIGN KEY (MaKhachHang) REFERENCES KhachHang(MaKhachHang),
    FOREIGN KEY (SoKhung) REFERENCES XeMay(SoKhung)
);
GO


CREATE TABLE TaiKhoan (
    TenDangNhap NVARCHAR(50) PRIMARY KEY,
    MatKhau NVARCHAR(255) NOT NULL, 
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
INSERT INTO  (MaVatLieu, LoaiVatLieu, TenVatLieu, GiaBan) VALUES
('SK1111', N'Gạch xây', N'Gạch đỏ', 1500),
('SK1112', N'Gạch xây', N'Gạch block', 1000),
('SK1113', N'Thép tấm', N'Thép tấm', 30000),
('SK1114', N'Thép vật mạ kẽm', N'Thép hộp', 48000),
('SK1115', N'Sơn nước', N'Sơn nước jotun', 259000),
('SK1116', N'Sơn nội thất', N'Sơn Dolux nội thất',38900000 ),
('SK1117', N'Trần', N'Trần thạch cao',130000 ),

GO

-- 3. Thêm dữ liệu Bảng Khách Hàng (Nhập mã tay KH01, KH02...)
INSERT INTO KhachHang (MaKhachHang, HoTen, SoDienThoai, DiaChi, CCCD) VALUES
('KH01', N'Nguyễn Văn D', '0988111222', N'Quận 5, TP.HCM', '079123456789'),
('KH02', N'Trần Thị F', '0988333444', N'Quận 1, TP.HCM', '079987654321'),
('KH03', N'Lê Văn E', '0988555666', N'Thủ Đức, TP.HCM', '079111222333'),
('KH04', N'Phạm Thị M', '0988777888', N'Bình Thạnh, TP.HCM', '079444555666');
GO

-- 4. Thêm dữ liệu Bảng Hóa Đơn (Giả lập 2 xe đã bán: SK1111 và SK3333)
-- Lưu ý: Mã hóa đơn nhập tay (HD01, HD02...)
INSERT INTO HoaDon (MaHoaDon, MaNhanVien, MaKhachHang, MaVatLieu, NgayBan, TongTien, GhiChu) VALUES
('HD01', 'NV03', 'KH01', 'SK1111', '2024-01-15', 36000000, N'Trống'),
('HD02', 'NV03', 'KH02', 'SK1113', '2024-02-20', 18500000, N'Trống');
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
 select *from VatLieu
 select *from KhachHang
 select *from TaiKhoan
