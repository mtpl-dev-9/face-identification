# Check Your Database Structure

## Error Found
```
Unknown column 'mtpl_users.userEmployeeCode' in 'field list'
```

This means your `mtpl_users` table has different column names than expected.

## Steps to Fix:

### 1. Check Your Table Structure

Open phpMyAdmin (`http://localhost/phpmyadmin`) and run:

```sql
DESCRIBE mtpl_users;
```

### 2. Common Possibilities:

Your table might have columns like:
- `employee_code` (snake_case) instead of `userEmployeeCode` (camelCase)
- `emp_code` 
- `code`
- Or completely different names

### 3. Share the Output

Once you run `DESCRIBE mtpl_users;`, share the column names so I can update the User model correctly.

### 4. Temporary Workaround

If you want to continue testing, you can:

1. Add the missing column:
```sql
ALTER TABLE mtpl_users 
ADD COLUMN userEmployeeCode VARCHAR(50) AFTER userLastName;
```

2. Or tell me your actual column names and I'll update the model.

## What We Need

The `mtpl_users` table should have at least:
- User ID column
- First name column  
- Last name column
- **Employee code column** (this is what's missing/different)
- Active status column

Please share the actual column names from your database.
