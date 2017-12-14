
import matplotlib

# don't take all the data, but from 1/3 of the data up to 2/3
# of the data
begin = int(m.floor(len(rx)/3))
end = int((2*m.floor(len(rx)/3)))

# plot the detected gesture
plt.plot( lx [begin:end] , ly[begin:end] , 'ro−' )
plt.plot( lx [begin] , ly[begin] , 'bo' ,ms =10)
plt.plot( lx [end] , ly[end] , 'o' ,ms=10 , c= 'black' )
plt.plot( rx [begin:end] , ry[begin:end] , ' g+−' )
plt.plot( rx [begin] , ry [begin] , 'bo' ,ms =10)
plt.plot(rx[end], ry[end],'o',ms=10,c='black')
