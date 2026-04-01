class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True)
    icon = Column(String(50)) # For the UI (e.g., FontAwesome class)
    image_url = Column(String(255), nullable=True)