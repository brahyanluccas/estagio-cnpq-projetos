from app import app, db 
from moldes import (Resposta, MembroEquipe, OrganizacaoParceira, RecursoAlavancado, 
                    ContratoTecnologia, AcordoNDA, CooperacaoInternacional, 
                    PesquisadorVisitante, EventoOrganizado, MetaProgresso, Usuario)

def limpar_todas_as_tabelas():
    with app.app_context():
        print("Iniciando a limpeza do banco de dados...")
        
        try:
            db.session.execute(db.text('PRAGMA foreign_keys = OFF;'))
            
            for table in reversed(db.metadata.sorted_tables):
                print(f"Limpando tabela: {table.name}...")
                db.session.execute(table.delete())
            
            print("Limpando a tabela de usuários...")
            db.session.query(Usuario).delete()

            db.session.commit()
            
            print("\n✅ Banco de dados limpo com sucesso! Todos os dados foram apagados.")

        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Ocorreu um erro ao limpar o banco de dados: {e}")
        finally:
            db.session.execute(db.text('PRAGMA foreign_keys = ON;'))

if __name__ == '__main__':
    confirmacao = input("ATENÇÃO: Isso apagará TODOS os dados do banco. Você tem certeza? (s/N): ")
    if confirmacao.lower() == 's':
        limpar_todas_as_tabelas()
    else:
        print("Operação cancelada.")