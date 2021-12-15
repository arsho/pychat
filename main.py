from Header import *
import Gui
import Utils
import Console

if len(sys.argv) > 1 and sys.argv[1] == "-cli":
    root = Console.Console()
else:
    root = Gui.Gui()
Utils.load_contacts()
root.mainloop()
Utils.dump_contacts() # when program destroyed
