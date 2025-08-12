import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

# Configuração do banco
CAMINHO_BD = "tarefas.db"
FORMATO_DATA = "%Y-%m-%d %H:%M"

def obter_conexao():
    conexao = sqlite3.connect(CAMINHO_BD)
    return conexao

def criar_tabela():
    conexao = obter_conexao()
    cursor = conexao.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tarefas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        descricao TEXT,
        datahora TEXT,
        concluida INTEGER DEFAULT 0
    )
    """)
    conexao.commit()
    conexao.close()

def carregar_tarefas():
    conexao = obter_conexao()
    cursor = conexao.cursor()
    cursor.execute("SELECT id, titulo, datahora, concluida FROM tarefas ORDER BY datahora")
    tarefas = cursor.fetchall()
    conexao.close()
    return tarefas

def adicionar_tarefa(titulo, descricao, datahora):
    conexao = obter_conexao()
    cursor = conexao.cursor()
    cursor.execute("INSERT INTO tarefas (titulo, descricao, datahora) VALUES (?, ?, ?)",
                (titulo, descricao, datahora))
    conexao.commit()
    conexao.close()

def editar_tarefa(id_tarefa, titulo, descricao, datahora):
    conexao = obter_conexao()
    cursor = conexao.cursor()
    cursor.execute("UPDATE tarefas SET titulo=?, descricao=?, datahora=? WHERE id=?",
                (titulo, descricao, datahora, id_tarefa))
    conexao.commit()
    conexao.close()

def excluir_tarefa(id_tarefa):
    conexao = obter_conexao()
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM tarefas WHERE id=?", (id_tarefa,))
    conexao.commit()
    conexao.close()

def concluir_tarefa(id_tarefa):
    conexao = obter_conexao()
    cursor = conexao.cursor()
    cursor.execute("UPDATE tarefas SET concluida=1 WHERE id=?", (id_tarefa,))
    conexao.commit()
    conexao.close()

def obter_detalhes_tarefa(id_tarefa):
    conexao = obter_conexao()
    cursor = conexao.cursor()
    cursor.execute("SELECT titulo, descricao, datahora, concluida FROM tarefas WHERE id=?", (id_tarefa,))
    tarefa = cursor.fetchone()
    conexao.close()
    return tarefa

# ---------------- INTERFACE ----------------
class GerenciadorTarefas(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gerenciador de Tarefas")
        self.geometry("700x400")
        self.configure(bg="#2C3E50")

        self.criar_widgets()
        self.atualizar_lista()

    def criar_widgets(self):
        frame_top = tk.Frame(self, bg="#2C3E50")
        frame_top.pack(pady=10)

        tk.Label(frame_top, text="Título:", bg="#2C3E50", fg="white").grid(row=0, column=0, padx=5)
        self.entry_titulo = tk.Entry(frame_top, width=25)
        self.entry_titulo.grid(row=0, column=1, padx=5)

        tk.Label(frame_top, text="Data/Hora:", bg="#2C3E50", fg="white").grid(row=0, column=2, padx=5)
        self.entry_data = tk.Entry(frame_top, width=20)
        self.entry_data.grid(row=0, column=3, padx=5)

        tk.Label(frame_top, text="Descrição:", bg="#2C3E50", fg="white").grid(row=1, column=0, padx=5, pady=5)
        self.entry_desc = tk.Entry(frame_top, width=60)
        self.entry_desc.grid(row=1, column=1, columnspan=3, padx=5, pady=5)

        frame_buttons = tk.Frame(self, bg="#2C3E50")
        frame_buttons.pack(pady=5)

        ttk.Button(frame_buttons, text="Adicionar", command=self.adicionar, style="Green.TButton").grid(row=0, column=0, padx=5)
        ttk.Button(frame_buttons, text="Editar", command=self.editar, style="Blue.TButton").grid(row=0, column=1, padx=5)
        ttk.Button(frame_buttons, text="Excluir", command=self.excluir, style="Red.TButton").grid(row=0, column=2, padx=5)
        ttk.Button(frame_buttons, text="Concluir", command=self.concluir, style="Orange.TButton").grid(row=0, column=3, padx=5)

        self.tree = ttk.Treeview(self, columns=("ID", "Título", "Data", "Status"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Título", text="Título")
        self.tree.heading("Data", text="Data/Hora")
        self.tree.heading("Status", text="Status")
        self.tree.column("ID", width=30)
        self.tree.column("Título", width=200)
        self.tree.column("Data", width=130)
        self.tree.column("Status", width=100)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)

        self.tree.bind("<Double-1>", self.mostrar_detalhes)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background="#34495E", foreground="white", fieldbackground="#34495E", rowheight=25)
        style.configure("Green.TButton", background="green", foreground="white")
        style.configure("Blue.TButton", background="blue", foreground="white")
        style.configure("Red.TButton", background="red", foreground="white")
        style.configure("Orange.TButton", background="orange", foreground="white")

    def atualizar_lista(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for tarefa in carregar_tarefas():
            status = "Concluída" if tarefa[3] else "Pendente"
            self.tree.insert("", tk.END, values=(tarefa[0], tarefa[1], tarefa[2], status))

    def adicionar(self):
        titulo = self.entry_titulo.get()
        descricao = self.entry_desc.get()
        data = self.entry_data.get()

        if not titulo or not data:
            messagebox.showerror("Erro", "Título e Data/Hora são obrigatórios!")
            return

        try:
            datetime.strptime(data, FORMATO_DATA)
        except ValueError:
            messagebox.showerror("Erro", "Formato da data inválido! Use YYYY-MM-DD HH:MM")
            return

        adicionar_tarefa(titulo, descricao, data)
        self.atualizar_lista()

    def editar(self):
        item = self.tree.selection()
        if not item:
            messagebox.showerror("Erro", "Selecione uma tarefa para editar.")
            return
        id_tarefa = self.tree.item(item)["values"][0]

        titulo = self.entry_titulo.get()
        descricao = self.entry_desc.get()
        data = self.entry_data.get()

        if not titulo or not data:
            messagebox.showerror("Erro", "Título e Data/Hora são obrigatórios!")
            return

        editar_tarefa(id_tarefa, titulo, descricao, data)
        self.atualizar_lista()

    def excluir(self):
        item = self.tree.selection()
        if not item:
            messagebox.showerror("Erro", "Selecione uma tarefa para excluir.")
            return
        id_tarefa = self.tree.item(item)["values"][0]
        excluir_tarefa(id_tarefa)
        self.atualizar_lista()

    def concluir(self):
        item = self.tree.selection()
        if not item:
            messagebox.showerror("Erro", "Selecione uma tarefa para concluir.")
            return
        id_tarefa = self.tree.item(item)["values"][0]
        concluir_tarefa(id_tarefa)
        self.atualizar_lista()

    def mostrar_detalhes(self, event):
        item = self.tree.selection()
        if not item:
            return
        id_tarefa = self.tree.item(item)["values"][0]
        tarefa = obter_detalhes_tarefa(id_tarefa)
        if tarefa:
            detalhes = f"Título: {tarefa[0]}\nData/Hora: {tarefa[2]}\nStatus: {'Concluída' if tarefa[3] else 'Pendente'}\n\nDescrição:\n{tarefa[1]}"
            messagebox.showinfo("Detalhes da Tarefa", detalhes)

if __name__ == "__main__":
    criar_tabela()
    app = GerenciadorTarefas()
    app.mainloop()
import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

# -------------------------
# Banco de dados
# -------------------------
def criar_bd():
    conexao = sqlite3.connect("tarefas.db")
    cursor = conexao.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descricao TEXT,
            datahora TEXT,
            concluida INTEGER DEFAULT 0
        )
    """)
    conexao.commit()
    conexao.close()

def inserir_tarefa(titulo, descricao, datahora):
    conexao = sqlite3.connect("tarefas.db")
    cursor = conexao.cursor()
    cursor.execute("INSERT INTO tarefas (titulo, descricao, datahora) VALUES (?, ?, ?)",
                (titulo, descricao, datahora))
    conexao.commit()
    conexao.close()

def listar_tarefas():
    conexao = sqlite3.connect("tarefas.db")
    cursor = conexao.cursor()
    cursor.execute("SELECT * FROM tarefas ORDER BY datahora")
    tarefas = cursor.fetchall()
    conexao.close()
    return tarefas

def atualizar_tarefa(id_tarefa, titulo, descricao, datahora):
    conexao = sqlite3.connect("tarefas.db")
    cursor = conexao.cursor()
    cursor.execute("UPDATE tarefas SET titulo=?, descricao=?, datahora=? WHERE id=?",
                (titulo, descricao, datahora, id_tarefa))
    conexao.commit()
    conexao.close()

def excluir_tarefa(id_tarefa):
    conexao = sqlite3.connect("tarefas.db")
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM tarefas WHERE id=?", (id_tarefa,))
    conexao.commit()
    conexao.close()

def concluir_tarefa(id_tarefa):
    conexao = sqlite3.connect("tarefas.db")
    cursor = conexao.cursor()
    cursor.execute("UPDATE tarefas SET concluida=1 WHERE id=?", (id_tarefa,))
    conexao.commit()
    conexao.close()

# -------------------------
# Interface Tkinter
# -------------------------
def atualizar_lista():
    for item in tree.get_children():
        tree.delete(item)
    for tarefa in listar_tarefas():
        cor = "#d4fcd4" if tarefa[4] == 1 else "#fcd4d4"
        tree.insert("", tk.END, values=(tarefa[0], tarefa[1], tarefa[3], "Concluída" if tarefa[4] else "Pendente"), tags=("cor",))
        tree.tag_configure("cor", background=cor)

def abrir_detalhes(event):
    item = tree.selection()
    if not item:
        return
    tarefa_id = tree.item(item, "values")[0]
    conexao = sqlite3.connect("tarefas.db")
    cursor = conexao.cursor()
    cursor.execute("SELECT descricao FROM tarefas WHERE id=?", (tarefa_id,))
    descricao = cursor.fetchone()[0]
    conexao.close()
    messagebox.showinfo("Descrição da Tarefa", descricao if descricao else "Sem descrição.")

def adicionar_tarefa():
    def salvar():
        titulo = entry_titulo.get()
        descricao = entry_descricao.get("1.0", tk.END).strip()
        datahora = entry_datahora.get()
        try:
            datetime.strptime(datahora, "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showerror("Erro", "Formato de data/hora inválido! Use YYYY-MM-DD HH:MM")
            return
        inserir_tarefa(titulo, descricao, datahora)
        atualizar_lista()
        janela_add.destroy()

    janela_add = tk.Toplevel(root)
    janela_add.title("Adicionar Tarefa")
    janela_add.geometry("400x300")

    tk.Label(janela_add, text="Título:").pack()
    entry_titulo = tk.Entry(janela_add, width=40)
    entry_titulo.pack()

    tk.Label(janela_add, text="Descrição:").pack()
    entry_descricao = tk.Text(janela_add, width=40, height=5)
    entry_descricao.pack()

    tk.Label(janela_add, text="Data e hora (YYYY-MM-DD HH:MM):").pack()
    entry_datahora = tk.Entry(janela_add, width=40)
    entry_datahora.pack()

    tk.Button(janela_add, text="Salvar", bg="green", fg="white", command=salvar).pack(pady=10)

def editar_tarefa():
    item = tree.selection()
    if not item:
        messagebox.showerror("Erro", "Selecione uma tarefa para editar.")
        return
    tarefa_id = tree.item(item, "values")[0]
    conexao = sqlite3.connect("tarefas.db")
    cursor = conexao.cursor()
    cursor.execute("SELECT titulo, descricao, datahora FROM tarefas WHERE id=?", (tarefa_id,))
    titulo, descricao, datahora = cursor.fetchone()
    conexao.close()

    def salvar():
        novo_titulo = entry_titulo.get()
        nova_descricao = entry_descricao.get("1.0", tk.END).strip()
        nova_datahora = entry_datahora.get()
        try:
            datetime.strptime(nova_datahora, "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showerror("Erro", "Formato de data/hora inválido! Use YYYY-MM-DD HH:MM")
            return
        atualizar_tarefa(tarefa_id, novo_titulo, nova_descricao, nova_datahora)
        atualizar_lista()
        janela_edit.destroy()

    janela_edit = tk.Toplevel(root)
    janela_edit.title("Editar Tarefa")
    janela_edit.geometry("400x300")

    tk.Label(janela_edit, text="Título:").pack()
    entry_titulo = tk.Entry(janela_edit, width=40)
    entry_titulo.insert(0, titulo)
    entry_titulo.pack()

    tk.Label(janela_edit, text="Descrição:").pack()
    entry_descricao = tk.Text(janela_edit, width=40, height=5)
    entry_descricao.insert("1.0", descricao)
    entry_descricao.pack()

    tk.Label(janela_edit, text="Data e hora (YYYY-MM-DD HH:MM):").pack()
    entry_datahora = tk.Entry(janela_edit, width=40)
    entry_datahora.insert(0, datahora)
    entry_datahora.pack()

    tk.Button(janela_edit, text="Salvar", bg="blue", fg="white", command=salvar).pack(pady=10)

def deletar_tarefa():
    item = tree.selection()
    if not item:
        messagebox.showerror("Erro", "Selecione uma tarefa para excluir.")
        return
    tarefa_id = tree.item(item, "values")[0]
    if messagebox.askyesno("Confirmar", "Tem certeza que deseja excluir esta tarefa?"):
        excluir_tarefa(tarefa_id)
        atualizar_lista()

def concluir_tarefa_btn():
    item = tree.selection()
    if not item:
        messagebox.showerror("Erro", "Selecione uma tarefa para concluir.")
        return
    tarefa_id = tree.item(item, "values")[0]
    concluir_tarefa(tarefa_id)
    atualizar_lista()

# -------------------------
# Inicialização
# -------------------------
criar_bd()
root = tk.Tk()
root.title("Gerenciador de Tarefas")
root.geometry("600x400")
root.configure(bg="#f0f0f0")

# Lista
tree = ttk.Treeview(root, columns=("ID", "Título", "Data/Hora", "Status"), show="headings")
tree.heading("ID", text="ID")
tree.heading("Título", text="Título")
tree.heading("Data/Hora", text="Data/Hora")
tree.heading("Status", text="Status")
tree.bind("<Double-1>", abrir_detalhes)
tree.pack(fill=tk.BOTH, expand=True, pady=10)

# Botões
frame_botoes = tk.Frame(root, bg="#f0f0f0")
frame_botoes.pack()

tk.Button(frame_botoes, text="Adicionar", bg="green", fg="white", command=adicionar_tarefa).grid(row=0, column=0, padx=5)
tk.Button(frame_botoes, text="Editar", bg="blue", fg="white", command=editar_tarefa).grid(row=0, column=1, padx=5)
tk.Button(frame_botoes, text="Concluir", bg="orange", fg="white", command=concluir_tarefa_btn).grid(row=0, column=2, padx=5)
tk.Button(frame_botoes, text="Excluir", bg="red", fg="white", command=deletar_tarefa).grid(row=0, column=3, padx=5)

atualizar_lista()
root.mainloop()
