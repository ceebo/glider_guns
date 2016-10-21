from os import listdir

guns = {}
tentative_guns = []
stats = {'fixed' : 0, 'test' : 0}
confirmed = set()

#if s2 is in s1 return the following number otherwise return 1
def number_after(s1, s2):

    i = s1.find(s2)

    if i < 0:
        return 1

    ret = 0
    i += len(s2)

    while s1[i].isdigit():
        ret = 10 * ret + int(s1[i])
        i += 1

    return ret

def add_gun(period, area, desc):

    if period in guns and guns[period][0] <= area:
        return False

    if "%s_p%05d" % (desc, period) in confirmed:
        return False

    guns[period] = (area, desc)

    return True

def divisors(n, compression):
    for x in range(1, n // compression + 1):
        if n % x == 0:
            yield n // x

def add_variable_gun(base, x, y, compression, x_slack, y_slack,
                     x_trips, y_trips, x_overhang, y_overhang,
                     weird_x, weird_y, osc, osc_mod, factor, name):
    
    for d in range(100):

        add_x = (max(d - x_slack, 0) + x_trips - 1) // x_trips
        add_x -= min(d, x_overhang)
        add_x += weird_x.count(d)

        add_y = (max(d - y_slack, 0) + y_trips - 1) // y_trips
        add_y -= min(d, y_overhang)
        add_y += weird_y.count(d)

        area = (x + add_x) * (y + add_y)
        for p in divisors(base + 8 * d, compression):
            if p % osc in osc_mod:
                add_gun(p * factor, area, name + "_" + str(d))

# examine variable guns
for filename in sorted(listdir("variable")):
    try:
        if filename[-4:] != ".rle":
            continue

        period = int(filename[1:6])
        compression = None
        tentative_compression = None
        x_slack = y_slack = 0
        x_trips = y_trips = 1
        x_overhang = y_overhang = 0
        weird_x = weird_y = []
        osc_mod = [0]

        factor = number_after(filename, "x")
        osc = number_after(filename, "osc")

        for line in open("variable/" + filename):
            if line[0] == 'x':
                line = line.split(" ")
                x = int(line[2][:-1])
                y = int(line[5][:-1])
            elif "tentative_compression" in line:
                tentative_compression = int(line.split()[-1])
            elif "compression" in line:
                compression = int(line.split()[-1])
            elif "x_slack" in line:
                x_slack = int(line.split()[-1])
            elif "y_slack" in line:
                y_slack = int(line.split()[-1])
            elif "x_trips" in line:
                x_trips = int(line.split()[-1])
            elif "y_trips" in line:
                y_trips = int(line.split()[-1])
            elif "x_overhang" in line:
                x_overhang = int(line.split()[-1])
            elif "y_overhang" in line:
                y_overhang = int(line.split()[-1])
            elif "weird_x" in line:
                weird_x = eval(line.split("=")[-1])
            elif "weird_y" in line:
                weird_y = eval(line.split("=")[-1])
            elif "osc_mod" in line:
                osc_mod = eval(line.split("=")[-1])

        gun_data = [period, x, y, compression, x_slack, y_slack,
                    x_trips, y_trips, x_overhang, y_overhang,
                    weird_x, weird_y, osc, osc_mod, factor, filename[:-4]]

        stats[filename[:-4]] = 0
        add_variable_gun(*gun_data)
        
        if tentative_compression is not None:
            gun_data[3] = tentative_compression
            tentative_guns.append(gun_data)

    except:
        print "Problem with gun %s" % filename
        raise

# examine tentative suggestions that have been confirmed
for filename in listdir("confirmed"):
    try:
        if filename[-4:] != ".rle":
            continue

        period = int(filename[-9:-4])
        for line in open("confirmed/" + filename):
            if line[0] == 'x':
                line = line.split(" ")
                area = int(line[2][:-1]) * int(line[5][:-1])
                confirmed.add(filename[:-4])
                add_gun(period, area, filename[:-4])
    except:
        print "***** Problem with gun %s" % filename
        raise

# examine fixed guns
for filename in listdir("fixed"):
    try:
        if filename[-4:] != ".rle":
            continue

        period = int(filename[1:6])
        for line in open("fixed/" + filename):
            if line[0] == 'x':
                line = line.split(" ")
                area = int(line[2][:-1]) * int(line[5][:-1])
                improve = add_gun(period, area, "fixed")
                if not improve:
#                    pass
                    print filename
    except:
        print "***** Problem with gun %s" % filename
        raise

# examine test guns
for filename in listdir("test"):
    try:
        if filename[-4:] != ".rle":
            continue

        period = int(filename[1:6])
        for line in open("test/" + filename):
            if line[0] == 'x':
                line = line.split(" ")
                area = int(line[2][:-1]) * int(line[5][:-1])
                for signals in range(1, 10):
                    if period % signals == 0 and period >= 74 * signals:
                        add_gun(period // signals, area, "test")
    except:
        print "***** Problem with gun %s" % filename
        raise

total = number = 0
for period in guns:
    if 78 <= period < 1000:
        total += guns[period][0]
        number += 1

print "************************************"
print "Average area in range p78-999 = %d" % (total // number)
print "************************************"
print ""

print "*******************************"
print "Hall of Shame (p78 or greater)"
print "*******************************"

lines = 0
for period in sorted(guns, key=guns.get, reverse=True):
    if 78 <= period < 1000:
        print period, str(guns[period]).ljust(32), "(%d mod 8)" % (period % 8)
        lines += 1
        if lines == 20:
            break

print ""
print "*******************************"
print "Hall of Pain (p39 to p77)"
print "*******************************"

lines = 0
for period in sorted(guns, key=guns.get, reverse=True):
    if 39 <= period < 78:
        print period, guns[period][0]
        lines += 1
        if lines == 20:
            break

print ""
print "*******************************"
print "Hall of the Insane (p14 to p38)"
print "*******************************"

lines = 0
for period in sorted(guns, key=guns.get, reverse=True):
    if 14 <= period < 39:
        print period, guns[period][0]
        lines += 1
        if lines == 20:
            break

print ""
print "*************"
print "Gun List"
print "*************"

for period in sorted(guns):
    if period < 1000:
        gun_type = guns[period][1].split("_")[0]
        stats[gun_type] += 1
        print period, guns[period]

print ""
print "*************"
print "Stats"
print "*************"

for gun_type in sorted(stats, key=stats.get, reverse=True):
    print "%-*s%d" % (16, gun_type, stats[gun_type])

print "variable        %d" % (1000 - 14 - stats["fixed"])

for period in guns:
    guns[period] = guns[period][0], ""

for gun in tentative_guns:
    add_variable_gun(*gun)

print ""
print "*************"
print "Tentative guns"
print "*************"

for period in guns:
    if period < 1000 and guns[period][1]:
        print period, guns[period]


#print ""
#print "***********"
#print "Mod 8 stats"
#print "***********"
#mod8stats = [[0] * 9 for _ in range(8)]
#for period in guns:
#    mod8stats[period%8][period%9] = guns[period][0]
#    if period % 8 == 0:
#        print period, ",",
#    if all(mod8stats[period%8]):
#        print sum(mod8stats[period%8]) // 9, ",",
#    if period % 8 == 7:
#        print ""
#    if period == 999:
#        break
#
#print "***********"
#print "Possible x3"
#print "***********"
#
#for period in guns:
#    if period < 350 and period % 15 in [5, 10]:
#        print period, guns[period][0], guns[period*3][0], guns[period*3][0] * 1./guns[period][0]
