# Sự kiện khi app khởi động
@app.on_event("startup")
def on_startup():
    print("✅ Kết nối đến MySQL thành công!")
    models.Base.metadata.create_all(bind=engine)  # Tạo bảng nếu chưa có
    db = SessionLocal()
    seed_roles.seed_roles(db)  # Seed 3 role mặc định
    db.close()