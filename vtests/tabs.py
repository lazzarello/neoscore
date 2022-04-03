from neoscore.common import *

neoscore.setup()


# 6 line tab

staff_1 = TabStaff(ORIGIN, None, Mm(100))
clef_1 = TabClef(ZERO, staff_1)

# Mockup for something that will probably be pulled into tab code
def add_fingering(x, string, finger):
    MusicText((x, staff_1.string_y(string)), staff_1, f"fingering{finger}")


add_fingering(Mm(5), 1, 1)
add_fingering(Mm(7), 1, 2)
add_fingering(Mm(7), 2, 1)
add_fingering(Mm(7), 3, 1)
add_fingering(Mm(7), 4, 2)
add_fingering(Mm(7), 5, 3)
add_fingering(Mm(7), 6, 0)
add_fingering(Mm(10), 1, 5)


# 4 line tab

staff_2 = TabStaff((ZERO, Mm(20)), None, Mm(100), line_count=4)
clef_2 = TabClef(ZERO, staff_2, "4stringTabClef")

neoscore.show()
