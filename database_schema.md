# Ma'lumotlar bazasi sxemasi

## Jadvallar

### 1. User (Foydalanuvchi)
- id: Integer, Primary Key
- username: String, Unique
- email: String, Unique
- hashed_password: String
- full_name: String
- role: Enum (admin, chef, manager)
- is_active: Boolean
- created_at: DateTime

### 2. Ingredient (Mahsulot)
- id: Integer, Primary Key
- name: String, Unique
- quantity: Float (gramm)
- min_quantity: Float (gramm) - ogohlantirish uchun minimal miqdor
- created_at: DateTime
- updated_at: DateTime

### 3. IngredientDelivery (Mahsulot yetkazib berish)
- id: Integer, Primary Key
- ingredient_id: Integer, Foreign Key -> Ingredient.id
- quantity: Float (gramm)
- delivery_date: DateTime
- created_by: Integer, Foreign Key -> User.id
- created_at: DateTime

### 4. Meal (Ovqat)
- id: Integer, Primary Key
- name: String, Unique
- description: String
- created_at: DateTime
- updated_at: DateTime
- created_by: Integer, Foreign Key -> User.id

### 5. MealIngredient (Ovqat tarkibi)
- id: Integer, Primary Key
- meal_id: Integer, Foreign Key -> Meal.id
- ingredient_id: Integer, Foreign Key -> Ingredient.id
- quantity: Float (gramm) - bir porsiya uchun kerak bo'lgan miqdor
- created_at: DateTime
- updated_at: DateTime

### 6. MealServing (Ovqat berish)
- id: Integer, Primary Key
- meal_id: Integer, Foreign Key -> Meal.id
- portions: Integer - berilgan porsiyalar soni
- served_at: DateTime
- served_by: Integer, Foreign Key -> User.id
- created_at: DateTime

### 7. MonthlyReport (Oylik hisobot)
- id: Integer, Primary Key
- month: Integer
- year: Integer
- total_portions_served: Integer
- total_portions_possible: Integer
- difference_percentage: Float
- created_at: DateTime
- updated_at: DateTime

### 8. Alert (Ogohlantirish)
- id: Integer, Primary Key
- message: String
- alert_type: Enum (ingredient_low, usage_suspicious)
- is_read: Boolean
- created_at: DateTime
- related_ingredient_id: Integer, Foreign Key -> Ingredient.id (nullable)
- related_report_id: Integer, Foreign Key -> MonthlyReport.id (nullable)

## Munosabatlar

1. User -> IngredientDelivery: Bir foydalanuvchi ko'p mahsulot yetkazib berishlarni yaratishi mumkin
2. User -> Meal: Bir foydalanuvchi ko'p ovqatlarni yaratishi mumkin
3. User -> MealServing: Bir foydalanuvchi ko'p ovqat berishlarni amalga oshirishi mumkin
4. Ingredient -> IngredientDelivery: Bir mahsulotga ko'p yetkazib berishlar bo'lishi mumkin
5. Ingredient -> MealIngredient: Bir mahsulot ko'p ovqatlar tarkibida bo'lishi mumkin
6. Meal -> MealIngredient: Bir ovqat ko'p mahsulotlardan tashkil topishi mumkin
7. Meal -> MealServing: Bir ovqat ko'p marta berilishi mumkin
8. Ingredient -> Alert: Bir mahsulot ko'p ogohlantirishlarga bog'liq bo'lishi mumkin
9. MonthlyReport -> Alert: Bir hisobot ko'p ogohlantirishlarga bog'liq bo'lishi mumkin
