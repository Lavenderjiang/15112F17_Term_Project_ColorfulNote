import tkinter

root = tkinter.Tk()
canvas = tkinter.Canvas(root)
canvas.grid(row = 0, column = 0)
photo = tkinter.PhotoImage(file = 'logo.gif')
canvas.create_image(50, 100, image=photo)
root.mainloop()