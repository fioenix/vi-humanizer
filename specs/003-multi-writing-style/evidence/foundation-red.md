# Foundation RED: style registry chưa có card

**Command**

```bash
python3 scripts/validate-package.py
```

**Exit**: `1`

**Output đã đọc**

```text
LỖI: Style card phải đúng thứ tự canonical ['ke-trai-nghiem', 'phoi-hop-cong-viec', 'chuyen-mon-cong-khai', 'marketing-thuyet-phuc', 'huong-dan-ky-thuat', 'van-hanh-doanh-nghiep', 'hoc-thuat-phan-tich'], đang là []
```

Kết luận: file registry, schema, package path và consumer markers đã được nhận diện. Gate chỉ còn đỏ vì chưa triển khai bảy card; đây là RED mong đợi trước US1.
