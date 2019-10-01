#!/usr/bin/python
import sys

# 20190709 SIMMOMA - Initial Prototype created to read Benchmark and spread fields
# 20190710 SIMMOMA - Added in all of Jim Jackson's requested fields
# 20190710 SIMMOMA - Added in the ability to take filenames as args
# 20190717 SIMMOMA - Handled the fractional indicators
# 20190719 SIMMOMA - Jim Jackson confirmed the required spreads: Bench, i, z, & oas. Not d.
#                  - d_spread removed from header and read and write operations.
# 20190722 SIMMOMA - Added an ASOF date to identify the data inside the files. 
# 20190722 SIMMOMA - Updated header. Changed TRANSACTION_NUMBER to ORDER_ID and DEALER_NAME to DEALER. 

def handle_frac_ind(frac_ind, value):
	# this function takes two strings that represent a float
	# and returns a formated string representing that float
	# special case formating:
	#	"-.nn" changed to"-0.nn" 
	# 	".nn" changed to "0.nn"
	# found some transactions with " " in the data files for both
	# Frac indicators and values, so all errors will return "0"
	s = "."
	fi = frac_ind.strip()
	v = value.strip()
	try:
		i = len(v)-int(fi)
		if fi != '0': 
			if (v[:1] == '-') or (i == 0):
				s = "0."
			v = v[:i]+s+v[i:]
	except:
		v = '0'
	finally:
		return v


def main():
	print 'AIM History File Reader'

	delim = "|" # default
	bp = 0 # byte pointer to keep track of location in the file
	header = ("ASOF_DATE"+delim+
			"ORDER_ID"+delim+
			"CUSIP"+delim+
			"TICKER"+delim+
			"COUPON"+delim+
			"MATURITY_DATE"+delim+
			"BUYSELL"+delim+
			"TRADE_DATE"+delim+
			"SETTLE_DATE"+delim+
			"PAR_AMT"+delim+
			"YIELD_AMT"+delim+
			"DEALER"+delim+
			"FUND_NUMBER"+delim+
			"BENCHMARK"+delim+
			"BENCHMARK_YIELD"+delim+
			"BENCHMARK_SPREAD"+delim+
			"I_SPREAD"+delim+
			"Z_SPREAD"+delim+
			"OAS_SPREAD")

	
	## file IO section **
	if len(sys.argv) < 3:
		print 'Useage: aimreader.py <input file> <asof date yyyymmdd> <output file (optional)>'
		exit()

	if len(sys.argv) == 3:
		ifile = sys.argv[1]
		asof_dt = sys.argv[2]
		ofile = ifile+".dsv"

	if len(sys.argv) == 4:
		ifile = sys.argv[1]
		asof_dt = sys.argv[2]
		ofile = sys.argv[3]

	try:
		fh = open(ifile, 'r')
		print 'Opening: ',fh.name
	except:
		print ifile+' not found. Be sure you are running this is the same folder as the input file.' 
		exit()

	try:	
		print 'Reading AIM History data from ',fh.name
		line = fh.readline().strip()
	except:
		print 'File is empty. No data to process.'
		exit()

	try:
		fh2 = open(ofile, 'w')
		print 'Opening: ',fh2.name
	except:
		print ofile+' couldnt be opened for writing, probably permissions related.'
		exit()

	print 'Writing file header to ',fh2.name
	fh2.write (header+'\n')

	print 'Writing AIM History data to ',fh2.name,' - ** This can take several minutes. **'

	## Data read section **
	while True:
		# Advance through the input file line by line and read bytes at specific offsets	

		fh.seek(bp)
		txn_nbr = fh.read(6)

		fh.seek(bp+10)
		cusip = fh.read(12)
		
		fh.seek(bp+43)
		ticker = fh.read(8)

		fh.seek(bp+52)
		coupon_frac_ind = fh.read(2)
		fh.seek(bp+55)
		# SIMMOMA - The next 2 lines could be done with the read in the function call, 
		# but I chose seperate instructions throughout the program for readability.
		coupon = fh.read(12)
		coupon = handle_frac_ind(coupon_frac_ind, coupon) 

		fh.seek(bp+68)
		maturity_date = fh.read(8) 
		
		fh.seek(bp+91)
		buysell = fh.read(1)

		fh.seek(bp+97)
		trd_date = fh.read(8)

		fh.seek(bp+115)
		set_date = fh.read(8)

		fh.seek(bp+124)
		par_frac_ind = fh.read(2)
		fh.seek(bp+127)
		par_amt = fh.read(12)
		par_amt = handle_frac_ind(par_frac_ind, par_amt)

		fh.seek(bp+140)
		yld_frac_ind = fh.read(2)
		fh.seek(bp+143)
		yld = fh.read(12)
		yld = handle_frac_ind(yld_frac_ind, yld)

		fh.seek(bp+207)
		dealer = fh.read(20)

		fh.seek(bp+561)
		fund_nbr = fh.read(7)

		fh.seek(bp+2258)
		bmark = fh.read(9)
		
		fh.seek(bp+2268)
		bmarkyld_frac_ind = fh.read(2)
		fh.seek(bp+2271)
		bmarkyield = fh.read(12)
		bmarkyield = handle_frac_ind(bmarkyld_frac_ind, bmarkyield)

		fh.seek(bp+2284)
		bmarksprd_frac_ind = fh.read(2)
		fh.seek(bp+2287)
		bmarkspread = fh.read(12) 
		bmarkspread = handle_frac_ind(bmarksprd_frac_ind, bmarkspread)

		fh.seek(bp+2316)
		ispread_frac_ind = fh.read(2)
		fh.seek(bp+2319)
		ispread = fh.read(12)
		ispread = handle_frac_ind(ispread_frac_ind, ispread)
		
		fh.seek(bp+2332)
		zspread_frac_ind = fh.read(2)
		fh.seek(bp+2335)
		zspread = fh.read(12)
		zspread = handle_frac_ind(zspread_frac_ind, zspread) 
		
		fh.seek(bp+2364)
		oaspread_frac_ind = fh.read(2)
		fh.seek(bp+2367)
		oasspread = fh.read(12)
		oasspread = handle_frac_ind(oaspread_frac_ind, oasspread)

		
		# Return the file pointer to the beginning of the current line
		fh.seek(bp) 

		#get the next line of input file until there are no more to read
		line = fh.readline().strip()
		if not line: 
			break
		
		# set the next byte pointer
		bp = fh.tell()-1 # back up 1 byte because of the \n char at the EOL


		# write out each transaction for just the converted 62xx accounts
		# exclude transactions with cusips since cusip is the primary search key
		if fund_nbr.strip()[0:2] == '62'and cusip.strip() != '':

			s = ( asof_dt.strip()+delim+
				txn_nbr.strip()+delim+
				cusip.strip()+delim+
				ticker.strip()+delim+
				coupon.strip()+delim+
				maturity_date.strip()+delim+
				buysell.strip()+delim+
				trd_date.strip()+delim+
				set_date.strip()+delim+
				par_amt.strip()+delim+
				yld.strip()+delim+
				dealer.strip()+delim+
				fund_nbr.strip()+delim+
				bmark.strip()+delim+
				bmarkyield.strip()+delim+
				bmarkspread.strip()+delim+
				ispread.strip()+delim+
				zspread.strip()+delim+
				oasspread.strip())

			fh2.write(s+'\n')
			
	#close the files

	fh.close()
	fh2.close()

	print('Output is successfull.\nAIM History File Reader exiting')

	sys.exit()

if __name__ == "__main__":
	main()
