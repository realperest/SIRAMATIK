
from sqlalchemy import create_engine, text

# Connection string
DB_URL = "postgresql://postgres.wyursjdrnnjabpfeucyi:qk4SEnyhu3NUk2@aws-1-eu-central-1.pooler.supabase.com:6543/postgres"

def fix_cihazlar_constraint():
    """
    cihazlar tablosuna eksik UNIQUE constraint ekler.
    
    Hata: ON CONFLICT (firma_id, mac_adresi) kullanılıyor ama bu sütunlarda
    UNIQUE constraint yok.
    """
    print("Connecting to database...")
    engine = create_engine(DB_URL)
    
    with engine.connect() as conn:
        try:
            # 1. Önce mevcut constraint'i kontrol et
            print("Checking existing constraints on siramatik.cihazlar...")
            result = conn.execute(text("""
                SELECT constraint_name, constraint_type 
                FROM information_schema.table_constraints 
                WHERE table_schema = 'siramatik' 
                AND table_name = 'cihazlar';
            """))
            
            constraints = result.fetchall()
            print(f"Found {len(constraints)} constraints:")
            for c in constraints:
                print(f"  - {c[0]} ({c[1]})")
            
            # 2. UNIQUE constraint ekle
            print("\nAdding UNIQUE constraint on (firma_id, mac_adresi)...")
            conn.execute(text("""
                ALTER TABLE siramatik.cihazlar 
                ADD CONSTRAINT cihazlar_firma_mac_unique 
                UNIQUE (firma_id, mac_adresi);
            """))
            
            conn.commit()
            print("\n✅ SUCCESS! UNIQUE constraint added.")
            
        except Exception as e:
            if "already exists" in str(e):
                print("\n✅ Constraint already exists, no action needed.")
            else:
                print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    fix_cihazlar_constraint()
