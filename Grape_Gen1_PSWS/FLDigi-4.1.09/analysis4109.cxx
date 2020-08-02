// ----------------------------------------------------------------------------
// anal.cxx  --  anal modem
//
// Copyright (C) 2006-2009
//		Dave Freese, W1HKJ
//
// This file is part of fldigi.
//
// Modified by J C Gibbons / N8OBJ - May 2019
// Added analysis file output modifications
// - Removed relative time from output file, added full ISO date/time stamp
// - Added keeping present days data is the file already exist when program started
//
// Fldigi is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// Fldigi is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with fldigi.  If not, see <http://www.gnu.org/licenses/>.
// ----------------------------------------------------------------------------

#include <config.h>

#include <string>
#include <cstdio>
#include <ctime>

#include "analysis.h"
#include "modem.h"
#include "misc.h"
#include "filters.h"
#include "fftfilt.h"
#include "digiscope.h"
#include "waterfall.h"
#include "main.h"
#include "fl_digi.h"

#include "timeops.h"
#include "debug.h"

//added for file support tasks 7-19-19 JC Gibbons N8OBJ
#include <iostream>
#include <fstream>

using namespace std;

static char msg1[80];

void anal::tx_init()
{
}

void anal::rx_init()
{
	phaseacc = 0;
	put_MODEstatus(mode);
}

void anal::init()
{
	modem::init();
	rx_init();
	set_scope_mode(Digiscope::RTTY);
}

anal::~anal()
{
	delete bpfilt;
	delete ffilt;
	delete afilt;
}

// used for checking file exists function
#define F_OK 0

void anal::creatfilename()
{
// Function to find or create the working directory [if not exist yet]
// also creates the filename that should be open for today's date [w and w/o full path]
// Create embedded date YYMMDD for file creation naming
	time_t now = time(NULL);
	gmtime_r(&now, &File_Start_Date);

// create the embedded filename date image as YYMMDD
	strftime((char*)FileDate,sizeof(FileDate),"%y%m%d", &File_Start_Date);

// create the embedded file date image as YYYY-MM-DD
	strftime((char*)FileData,sizeof(FileData),"%Y-%m-%d", &File_Start_Date);

// create the home directory path 
	string HomePath;
	HomePath = getenv("HOME");

// create the home directory path to the WWVdata filestructure
        string WWVDataPath;
        WWVDataPath = getenv("HOME");

// append new working path for data storage
        WWVDataPath += "/WWVdata/";

// check for directory and if not there create it

	if (fl_access(WWVDataPath.c_str(),F_OK) == -1)
	//directory does not exist, so create it
	{
	//	printf("\n\nDirectory %s does NOT exist - creating it\n", WWVDataPath.c_str() ); // diag line
		fl_make_path(WWVDataPath.c_str());
		fl_chmod(WWVDataPath.c_str(),0775);
	}
//	else
//	printf("\n\nDirectory %s does exist and will use it\n", WWVDataPath.c_str() ); // diag line

// create the new analysis file name
        OpenAnalalysisFile="analysis";

// embedded date YYMMDD
        OpenAnalalysisFile.append(FileDate);

// csv file type extension
        OpenAnalalysisFile.append(".csv");

// Full name with path
// Added new file naming and storage by N8OBJ 5-7-19
	analysisFilename = HomePath;
	analysisFilename += "/WWVdata/";
//	now have analysisFilename = "/home/username/WWVdata/";

// create new analysis file name w/o path [for display in status line]
	analysisFilename.append("analysis");

// embedded date YYMMDD
	analysisFilename.append(FileDate);

// csv file type extension
	analysisFilename.append(".csv");
// now have full path and filename for today's data file
// in variable analysisFilename

}

void anal::restart()
{
	double fhi = ANAL_BW * 1.1 / samplerate;
	double flo = 0.0;
	if (bpfilt)
		bpfilt->create_filter(flo, fhi);
	else
		bpfilt = new fftfilt(flo, fhi, 2048);

	set_bandwidth(ANAL_BW);

	ffilt->reset();
	afilt->reset();

	elapsed = 0.0;
	fout = 0.0;
	wf_freq = frequency;

	if (clock_gettime(CLOCK_REALTIME, &start_time) == -1) {
		LOG_PERROR("clock_gettime");
		abort();
	}

	passno = 0;
	dspcnt = DSP_CNT;
	for (int i = 0; i < PIPE_LEN; i++) pipe[i] = 0;

	if (write_to_csv) stop_csv();

	start_csv();

}

anal::anal()
{
	mode = MODE_ANALYSIS;

	samplerate = ANAL_SAMPLERATE;

	bpfilt = (fftfilt *)0;
	ffilt = new Cmovavg(FILT_LEN * samplerate);
	afilt = new Cmovavg(FILT_LEN * samplerate);

	creatfilename();

	cap &= ~CAP_TX;
	write_to_csv = false;

	restart();
}

void anal::clear_syncscope()
{
	set_scope(0, 0, false);
}

cmplx anal::mixer(cmplx in)
{
	cmplx z = cmplx( cos(phaseacc), sin(phaseacc)) * in;

	phaseacc -= TWOPI * frequency / samplerate;
	if (phaseacc < 0) phaseacc += TWOPI;

	return z;
}

void anal::start_csv()
{
        string OrgNamePath;
        string LatLonAltPath;
	string FreqStdPath;

        OrgNamePath = getenv("HOME");

        OrgNamePath += "/WWVdata/OrgName.txt";

        LatLonAltPath = getenv("HOME");

        LatLonAltPath += "/WWVdata/LatLonAlt.txt";

        FreqStdPath = getenv("HOME");

        FreqStdPath += "/WWVdata/FreqStd.txt";

        creatfilename();

        //read in the user info for the 1st line of this days data collection
        //read in the Organizations Name - if not found indicate so in name returned

        string OrgName;

        ifstream OrgNameFile (OrgNamePath);
        if (OrgNameFile.is_open())
        {
                getline (OrgNameFile,OrgName);
                OrgNameFile.close();
        }
        else
	{
		 OrgName = "NO OrgNam file";
	}

        //read in the user info for the 1st line of this days data collection
        //read in the frequency standard being used - if not found indicate so in name returned

        string FreqStd;

        ifstream FreqStdFile (FreqStdPath);
        if (FreqStdFile.is_open())
        {
                getline (FreqStdFile,FreqStd);
                FreqStdFile.close();
        }
        else
	{
		FreqStd = "Unknown Freq Ref";
	}

        //read in the Latitude, Longitude and Altidude info - if not found indicate so in position returned

        string LatLonAlt;

        ifstream LatLonAltFile (LatLonAltPath);
        if (LatLonAltFile.is_open())
        {
                getline (LatLonAltFile,LatLonAlt);
                LatLonAltFile.close();
        }
        else
	{
		LatLonAlt = "00.00000, -00.00000, 00.00000, NO LatLonAlt file";
	}

        //Open the data file for creation (write) operation
        //first check to see if already created  (and don't destroy the same days data already gathered)

	if (fl_access(analysisFilename.c_str(),F_OK) == 0)
	{
	// file exists! - use it and keep adding to it

	// indicate in status line that file write in progress
        put_status("Using existing analysis file");
//	printf("\n\nUsing existing %s analysis file\n\n", analysisFilename.c_str() );  //diag printout
	write_to_csv = true;  //say to do writes to file
	}

	else

	// file not there - create it and populate the header info into it
	{
	FILE *out = fl_fopen(analysisFilename.c_str(), "w"); //create [write] for new data file
		if (unlikely(!out)) {
			LOG_PERROR("fl_fopen");
			return;
	}

	// file opened - write out header info
        put_status("Creating analysis file");

	// Write out the initial header info line to the new .csv file

	// use for initial header containing full date YYYY-MM-DD (and each line has no date, just time)
	fprintf(out, "%s,%s,%s,%s\n",FileData,OrgName.c_str(),FreqStd.c_str(),LatLonAlt.c_str());

	// Use for initial header for date embedded in each line of data (so no date needed in 1st line of info)
//	fprintf(out, "%s,%s,%s\n",OrgName.c_str(),FreqStd.c_str(),LatLonAlt.c_str());

	// Create the headers for the columns in the .CSV file usage
	fprintf(out, "UTC,Freq,Freq Err,Vpk,dBV(Vpk)\n");

	fclose(out);

//	printf("Creating analysis file %s \n", analysisFilename.c_str());  //diag output
	write_to_csv = true;  //say to do writes to file
	}
}

void anal::stop_csv()
{
	write_to_csv = false;

// clear status line
	put_status("");
}

void anal::writeFile()
{
	if (!write_to_csv) return;

	time_t now = time(NULL);
	struct tm tm;

// put check for date rollover here
	gmtime_r(&now, &tm);
	char DateNow [10];

//   Create embedded date stamp in the YYMMDD format
	strftime((char*)DateNow,sizeof(DateNow),"%y%m%d", &tm);
//	printf("Date now is =%s\n",DateNow); //diag printout

// check if date rolled over
	if (tm.tm_mday != File_Start_Date.tm_mday)
	{
		start_csv();
	}
	FILE *out = fl_fopen(analysisFilename.c_str(), "a");
	if (unlikely(!out)) {
		LOG_PERROR("fl_fopen");
		return;
	}

// N8OBJ 5-7-19 changed 8.3f to 11.6f (more decimal places on signal strength - show uV level)
// Changed /added new .csv fields
//	for ref header is: fprintf(out, "UTC,Freq,Freq Err,Vpk,dB(Vpk)\n");

// diag print realltime results to terminal window as well  N8OBJ - 7-9-19

// Printed header with date YYYY-MM-DD
// So no date in each timestamp
	// diag for printing data output to term
//	printf("%02d:%02d:%02d, %13.3f, %6.3f, %8.6f, %6.2f\n",
//		tm.tm_hour, tm.tm_min, tm.tm_sec,
//		(wf->rfcarrier() + (wf->USB() ? 1.0 : -1.0) * (frequency + fout)), fout,
//		amp,  20.0 * log10( (amp == 0 ? 1e-6 : amp) ) );

	fprintf(out, "%02d:%02d:%02d, %13.3f, %6.3f, %8.6f, %6.2f\n",
		tm.tm_hour, tm.tm_min, tm.tm_sec,
		(wf->rfcarrier() + (wf->USB() ? 1.0 : -1.0) * (frequency + fout)), fout,
		amp, 20.0 * log10( (amp == 0 ? 1e-6 : amp) ) );

// Printed header with no date so need full date in timestamp YYYY-MM-DD
	// diag for printing data output to term
//        printf("%s %02d:%02d:%02d, %13.3f, %6.3f, %8.6f, %6.2f\n",
//		FileData, tm.tm_hour, tm.tm_min, tm.tm_sec,
//		(wf->rfcarrier() + (wf->USB() ? 1.0 : -1.0) * (frequency + fout)), fout,
//		amp,  20.0 * log10( (amp == 0 ? 1e-6 : amp) ) );

//	fprintf(out, "%s %02d:%02d:%02d, %13.3f, %6.3f, %8.6f, %6.2f\n",
//		FileData, tm.tm_hour, tm.tm_min, tm.tm_sec,
//		(wf->rfcarrier() + (wf->USB() ? 1.0 : -1.0) * (frequency + fout)), fout,
//		amp, 20.0 * log10( (amp == 0 ? 1e-6 : amp) ) );

	fclose(out);

//	indicate in status line the actual file name being written is in progress
	char StatusMsg [80];
	sprintf( StatusMsg, "Writing analysis file %s", OpenAnalalysisFile.c_str());
	put_status(StatusMsg);

}

int anal::rx_process(const double *buf, int len)
{
	cmplx z, *zp;
	double fin;
	int n = 0;

	if (wf_freq != frequency) {
		restart();
		set_scope(pipe, PIPE_LEN, false);
	}

	for (int i = 0; i < len; i++) {
// create analytic signal from sound card input samples
		z = cmplx( *buf, *buf );
		buf++;
// mix it with the audio carrier frequency to create a baseband signal
		z = mixer(z);
// low pass filter using Windowed Sinc - Overlap-Add convolution filter
		n = bpfilt->run(z, &zp);

		if (n) {
			for (int j = 0; j < n; j++) {
// measure phase difference between successive samples to determine
// the frequency of the baseband signal (+anal_baud or -anal_baud)
// see class cmplx definiton for operator %
			fin = arg( conj(prevsmpl) * zp[j] ) * samplerate / TWOPI;
			prevsmpl = zp[j];
// filter using moving average filter
			fout = ffilt->run(fin);
			amp  = afilt->run(abs(zp[j]));
			}
		} //else prevsmpl = z;
	}

	if (passno++ > 10) {
		dspcnt -= (1.0 * n / samplerate);

		if (dspcnt <= 0) {
			for (int i = 0; i < PIPE_LEN -1; i++)
				pipe[i] = pipe[i+1];

			double fdsp = fout / 4.0;
			if (fabs(fdsp) < 2.6) {
				elapsed += DSP_CNT - dspcnt;
				pipe[PIPE_LEN - 1] = fout / 4.0;
				set_scope(pipe, PIPE_LEN, false);

				if (wf->USB())
					snprintf(msg1, sizeof(msg1), "%13.3f", wf->rfcarrier() + frequency + fout );
				else
					snprintf(msg1, sizeof(msg1), "%13.3f", wf->rfcarrier() - frequency - fout );
				put_Status2(msg1, 2.0);
				writeFile();
			}
// reset the display counter & the pipe pointer
			dspcnt = DSP_CNT;
		}
	}
	return 0;
}

//=====================================================================
// anal transmit
//=====================================================================

int anal::tx_process()
{
	return -1;
}
