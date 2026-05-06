"""
Script to seed the database with sample data for ROGER - Valeria API
"""

import asyncio
import sys
from pathlib import Path

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.config.settings import settings
from app.features.authenticate.domain.user import User
from app.features.authenticate.domain.role import Role
from app.features.authenticate.infrastructure.adapters.user_repository import UserRepository
from app.features.authenticate.infrastructure.adapters.password_hasher import password_hasher
from app.features.view_images.domain.image import Image
from app.features.view_images.infrastructure.adapters.image_repository import ImageRepository


async def seed_users(session: AsyncSession):
    """Seed users."""
    print("\n[*] Seeding users...")

    from app.features.authenticate.infrastructure.persistence.user_model import UserModel

    user_repository = UserRepository(session)

    # Sample users
    users_data = [
        {
            "email": "admin@roger.cl",
            "username": "admin",
            "password": "admin123",
            "role": Role.ADMINISTRADOR,
            "full_name": "Administrador ROGER"
        },
        {
            "email": "curador@roger.cl",
            "username": "curador",
            "password": "curador123",
            "role": Role.CURADOR,
            "full_name": "Curador Principal"
        },
        {
            "email": "investigador@roger.cl",
            "username": "investigador",
            "password": "investigador123",
            "role": Role.INVESTIGADOR,
            "full_name": "Investigador UCN"
        },
        {
            "email": "user@roger.cl",
            "username": "user",
            "password": "user123",
            "role": Role.USUARIO_ESTANDAR,
            "full_name": "Usuario de Prueba"
        },
    ]

    for user_data in users_data:
        # Check if exists
        existing = await user_repository.get_by_email(user_data["email"])
        if existing:
            print(f"  [SKIP] User {user_data['email']} already exists, skipping")
            continue

        # Create user directly using UserModel to include username
        user_model = UserModel(
            email=user_data["email"],
            username=user_data["username"],
            hashed_password=password_hasher.hash(user_data["password"]),
            role=user_data["role"],
            full_name=user_data["full_name"],
            is_active=True,
            is_verified=True
        )

        session.add(user_model)
        await session.flush()
        print(f"  [OK] Created user: {user_data['email']} ({user_data['role'].value})")


async def seed_images(session: AsyncSession):
    """Seed sample images."""
    print("\n[*] Seeding images...")

    image_repository = ImageRepository(session)

    # Sample images from Robert Gerstmann's collection
    images_data = [
        {
            "title": "Retrato de un agricultor del Valle del Elqui",
            "file_path": "/storage/images/valle_elqui_agricultor_1930.jpg",
            "description": "Agricultor local en el Valle del Elqui, región de Coquimbo. La fotografía captura la vida rural de la época.",
            "year": 1930,
            "location": "Valle del Elqui, Coquimbo, Chile",
            "tags": ["retrato", "agricultura", "valle del elqui", "vida rural"],
            "metadata": {
                "tecnica": "Fotografía analógica",
                "formato": "Placa de vidrio",
                "dimension": "13x18 cm"
            }
        },
        {
            "title": "Vista panorámica del puerto de Valparaíso",
            "file_path": "/storage/images/valparaiso_puerto_1928.jpg",
            "description": "Vista general del puerto de Valparaíso desde uno de los cerros. Se aprecian los barcos en el muelle y la actividad portuaria característica de la época.",
            "year": 1928,
            "location": "Valparaíso, Chile",
            "tags": ["panorámica", "puerto", "valparaíso", "mar"],
            "metadata": {
                "tecnica": "Fotografía analógica",
                "formato": "Placa de vidrio",
                "dimension": "18x24 cm"
            }
        },
        {
            "title": "Iglesia de San Pedro de Atacama",
            "file_path": "/storage/images/san_pedro_atacama_iglesia_1932.jpg",
            "description": "La histórica iglesia colonial de San Pedro de Atacama, construida en adobe. Uno de los templos más antiguos del norte de Chile.",
            "year": 1932,
            "location": "San Pedro de Atacama, Antofagasta, Chile",
            "tags": ["arquitectura", "iglesia", "colonial", "atacama"],
            "metadata": {
                "tecnica": "Fotografía analógica",
                "formato": "Placa de vidrio",
                "dimension": "13x18 cm"
            }
        },
        {
            "title": "Mineros en la pampa salitrera",
            "file_path": "/storage/images/pampa_salitrera_mineros_1929.jpg",
            "description": "Grupo de mineros trabajando en una oficina salitrera del norte de Chile. Testimonio visual de la época del auge del salitre.",
            "year": 1929,
            "location": "Pampa salitrera, Tarapacá, Chile",
            "tags": ["minería", "salitre", "trabajadores", "industria"],
            "metadata": {
                "tecnica": "Fotografía analógica",
                "formato": "Placa de vidrio",
                "dimension": "13x18 cm",
                "contexto": "Época del auge salitrero"
            }
        },
        {
            "title": "Mercado de Arica",
            "file_path": "/storage/images/arica_mercado_1931.jpg",
            "description": "Escena del mercado central de Arica con vendedoras y productos locales. Muestra la vida cotidiana y el comercio en el norte de Chile.",
            "year": 1931,
            "location": "Arica, Chile",
            "tags": ["mercado", "comercio", "vida cotidiana", "arica"],
            "metadata": {
                "tecnica": "Fotografía analógica",
                "formato": "Placa de vidrio",
                "dimension": "13x18 cm"
            }
        },
        {
            "title": "Observatorio Cerro Calán",
            "file_path": "/storage/images/observatorio_cerro_calan_1933.jpg",
            "description": "Vista del Observatorio Astronómico Nacional de Chile en Cerro Calán, Santiago.",
            "year": 1933,
            "location": "Cerro Calán, Santiago, Chile",
            "tags": ["astronomía", "ciencia", "observatorio", "santiago"],
            "metadata": {
                "tecnica": "Fotografía analógica",
                "formato": "Placa de vidrio",
                "dimension": "18x24 cm"
            }
        },
        {
            "title": "Familia mapuche en la Araucanía",
            "file_path": "/storage/images/araucania_familia_mapuche_1934.jpg",
            "description": "Retrato de una familia mapuche en su ruca (vivienda tradicional) en la región de la Araucanía.",
            "year": 1934,
            "location": "Araucanía, Chile",
            "tags": ["pueblos originarios", "mapuche", "cultura", "familia"],
            "metadata": {
                "tecnica": "Fotografía analógica",
                "formato": "Placa de vidrio",
                "dimension": "13x18 cm",
                "nota": "Documento etnográfico de valor patrimonial"
            }
        },
        {
            "title": "Cordillera de los Andes desde Santiago",
            "file_path": "/storage/images/santiago_cordillera_1927.jpg",
            "description": "Vista de la majestuosa Cordillera de los Andes con nieve desde la ciudad de Santiago.",
            "year": 1927,
            "location": "Santiago, Chile",
            "tags": ["paisaje", "cordillera", "andes", "naturaleza"],
            "metadata": {
                "tecnica": "Fotografía analógica",
                "formato": "Placa de vidrio",
                "dimension": "18x24 cm"
            }
        }
    ]

    for img_data in images_data:
        # Check if exists by title
        existing = await image_repository.list(limit=1)
        title_exists = any(img.title == img_data["title"] for img in existing)

        if title_exists:
            print(f"  [SKIP] Image '{img_data['title']}' already exists, skipping")
            continue

        # Create image
        image = Image(
            title=img_data["title"],
            file_path=img_data["file_path"],
            description=img_data["description"],
            year=img_data["year"],
            location=img_data["location"],
            author="Robert Gerstmann",
            tags=img_data["tags"],
            metadata=img_data["metadata"],
            is_public=True
        )

        await image_repository.create(image)
        print(f"  [OK] Created image: {img_data['title']} ({img_data['year']})")


async def seed_database():
    """Seed the database with sample data."""
    print("=" * 60)
    print("ROGER - Database Seeder")
    print("=" * 60)
    
    # Create engine and session
    engine = create_async_engine(settings.database_url, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            # Seed users
            await seed_users(session)

            # Seed images
            # await seed_images(session)  # Temporarily disabled due to ImageRepository.list() error

            # TODO: Seed collections
            # TODO: Seed historical documents

            # Commit
            await session.commit()
            
            print("\n" + "=" * 60)
            print("[SUCCESS] Database seeding completed successfully!")
            print("=" * 60)
            
            print("\nDefault credentials:")
            print("  Admin:        admin@roger.cl / admin123")
            print("  Curador:      curador@roger.cl / curador123")
            print("  Investigador: investigador@roger.cl / investigador123")
            print("  Usuario:      user@roger.cl / user123")
            
        except Exception as e:
            print(f"\n[ERROR] Error seeding database: {str(e)}")
            await session.rollback()
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_database())
