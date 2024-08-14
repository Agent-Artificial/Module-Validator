# module_validator/database.py

from sqlalchemy import create_engine, Column, Integer, String, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class ModuleEntry(Base):
    __tablename__ = 'modules'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    version = Column(String)
    entry_point = Column(String, nullable=False)
    config = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<ModuleEntry(name={self.name}, version={self.version})>"


class CommandEntry(Base):
    __tablename__ = 'commands'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    module_name = Column(String, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<CommandEntry(name={self.name}, module_name={self.module_name})>"
    
    
class Database:
    def __init__(self, config):
        self.engine = create_engine(config['database_url'])
        self.Session = sessionmaker(bind=self.engine)

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def add_module(self, name, version, entry_point, config=None):
        session = self.Session()
        module = ModuleEntry(name=name, version=version, entry_point=entry_point, config=config)
        session.add(module)
        session.commit()
        session.close()

    def get_module(self, name):
        session = self.Session()
        module = session.query(ModuleEntry).filter_by(name=name).first()
        session.close()
        return module

    def update_module(self, name, version=None, entry_point=None, config=None):
        session = self.Session()
        module = session.query(ModuleEntry).filter_by(name=name).first()
        if module:
            if version:
                module.version = version
            if entry_point:
                module.entry_point = entry_point
            if config:
                module.config = config
            session.commit()
        session.close()

    def delete_module(self, name):
        session = self.Session()
        module = session.query(ModuleEntry).filter_by(name=name).first()
        if module:
            session.delete(module)
            session.commit()
        session.close()

    def list_modules(self):
        session = self.Session()
        modules = session.query(ModuleEntry).all()
        session.close()
        return modules

    def create_tables(self):
        Base.metadata.create_all(self.engine)
        
    def add_command(self, name, module_name, description=None):
        session = self.Session()
        command = CommandEntry(name=name, module_name=module_name, description=description)
        session.add(command)
        session.commit()
        session.close()

    def get_command(self, name):
        session = self.Session()
        command = session.query(CommandEntry).filter_by(name=name).first()
        session.close()
        return command

    def update_command(self, name, module_name=None, description=None):
        session = self.Session()
        command = session.query(CommandEntry).filter_by(name=name).first()
        if command:
            if module_name:
                command.module_name = module_name
            if description:
                command.description = description
            session.commit()
        session.close()

    def delete_command(self, name):
        session = self.Session()
        command = session.query(CommandEntry).filter_by(name=name).first()
        if command:
            session.delete(command)
            session.commit()
        session.close()

    def list_commands(self):
        session = self.Session()
        commands = session.query(CommandEntry).all()
        session.close()
        return commands