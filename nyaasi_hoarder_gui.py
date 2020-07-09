from nyaasi_hoarder import nyaasi_hoarder
import tkinter as tk


class nyaasi_hoarder_gui:
	def __init__(self, master):

		self.master = master

		self.createMainMenu(self.master)



	def createMainMenu(self, master):
		
		master.title("Nyaasi Hoarder")
		master.geometry("500x500")
		master.resizable(0,0)
		master.mainloop()


def main():
	mainMenu = tk.Tk()

	nyaasi_hoarder_gui(mainMenu)




if __name__ == "__main__":
	main()
