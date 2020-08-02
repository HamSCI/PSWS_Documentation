// ----------------------------------------------------------------------------
// anal.cxx  --  anal modem
//
// Copyright (C) 2006-2009
//		Dave Freese, W1HKJ
//
// This file is part of fldigi.
//
// Modifications by J C Gibbons / N8OBJ
//
// Inital mods to not loose data on restart/  - May 2019
// Added info.txt file option for control of header - Feb 2020
// Added analysis file output modifications - April 2020
// - Removed relative time from output file, added full ISO date/time stamp
// - Added keeping present days data is the file already exist when program started
// Implemented new file / data sructures for the new PSWS definition - June 2020
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

// added for file support tasks 2-18-20 JC Gibbons N8OBJ
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

void anal::createfilename()
{
// Function to find the working directory
// also creates the filename that should be open for today's date [w and w/o full path]

//	printf("\nEntering createfilename routine\n"); //diag pring

        // path names to working directories
        string HomePath;
        string PSWSBaseDir;
        string AnalysisDir;

       // File locations for metadata info
        HomePath = getenv("HOME");
        PSWSBaseDir = HomePath + "/PSWS/";
        AnalysisDir = PSWSBaseDir + "Srawdata/";

// Create embedded ISODateTime YYYY-MM-DDTHHMMSS for file creation naming
	time_t now = time(NULL);
	gmtime_r(&now, &File_Start_Date);

// Create embedded ISODateTime data image as YYYY-MM-DDTHH:MM:SS for file header info
	gmtime_r(&now, &File_Start_Data);

// create the embedded filename date&time image as YYMMDD (original date format)
	strftime((char*)FileDate,sizeof(FileDate),"%y%m%d", &File_Start_Date);

//	printf("\nFileDate = %s\n",FileDate);

// create the embedded date data image as YYYY-MM-DDTHH:MM:SSZ (ISO Date format)
	strftime((char*)FileData,sizeof(FileData),"%Y-%m-%dT%H:%M:%S", &File_Start_Data);

//        printf("\nFileData = %s\n",FileData);

// check for ~/PSWS/ directory and if not there create entire file structure

        if (fl_access(PSWSBaseDir.c_str(),F_OK) == -1)
        //base directory does not exist, so create it and all subdirectoriew
        {
	        put_status("~/PSWS/Srawdata/ does NOT EXIST!");
		printf("Cannot find %s\n", PSWSBaseDir.c_str());
		write_to_csv = false;  //say NO  writes to file
        }
        else
	        printf("\n\nPSWS Main Directory %s DOES EXIST and will use it!\n", PSWSBaseDir.c_str() ); // diag line

// now create the analysis file name structure for today's data
	OpenAnalalysisFile.assign("analysis").append(FileDate).append(".csv");

// diag print out full file name
//	printf("\nTodays fileName is: %s\n", OpenAnalalysisFile.c_str());
// diag print out path to file
//        printf("\nPath to fileName is: %s\n", AnalysisDir.c_str());

// Full name with path
// Added new file naming and storage by N8OBJ 4-24-20
	analysisFilename.assign(AnalysisDir).append(OpenAnalalysisFile);

// diag print out full path name
        printf("\nFull pathname is: %s\n", analysisFilename.c_str());
//	printf("\nExiting createfilename routine\n"); //diag print

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

	createfilename();

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
//	printf("\nEntering start_csv routine\n\n"); //diag pring

	double CalcFreq;
	unsigned int CalcFrqNum;

        // path names to working directories
        string HomePath;
        string PSWSBaseDir;
        string AnalysisDir;
        string PSWSinfoPath;
        string PSWSstatPath;
        string PSWScmdPath;
        string PSWScodePath;
        string PSWStempPath;
        string PSWSdataPath;
	string PSWSdataPathNew;

        // metadata file paths
        string CityStatePath;
        string CallSignPath;
        string LatLonElvPath;
        string FreqStdPath;
        string NodeNumPath;
        string GridSqrPath;
        string Radio1Path;
	string Radio1IDPath;
        string AntennaPath;
        string MetadataPath;
        string Beacon1Path;

        // variables to hold metadata read from files
        string CityState;
        string CallSign;
        string LatLonElv;
        string FreqStd;
        string NodeNum;
        string GridSqr;
        string Radio1;
	string Radio1ID;
        string Antenna;
        string Metadata;
        string DataTyp;
	string SavedBeacon1;
        string Beacon1;

       // File locations for metadata info
        HomePath = getenv("HOME");
        PSWSBaseDir = HomePath + "/PSWS/";
        AnalysisDir = PSWSBaseDir + "Srawdata/";
        PSWSinfoPath = PSWSBaseDir + "Sinfo/";
        PSWSstatPath = PSWSBaseDir + "Sstat/";
        PSWScmdPath = PSWSBaseDir + "Scmd/";
        PSWScodePath = PSWSBaseDir + "Scode/";
        PSWStempPath = PSWSBaseDir + "Stemp/";
        PSWSdataPath = PSWSBaseDir + "Sdata/";

        CityStatePath = PSWSinfoPath + "CityState.txt";
        CallSignPath = PSWSinfoPath + "CallSign.txt";
        LatLonElvPath = PSWSinfoPath + "LatLonElv.txt";
        FreqStdPath = PSWSinfoPath + "FreqStd.txt";
        NodeNumPath = PSWSinfoPath + "NodeNum.txt";
        GridSqrPath = PSWSinfoPath + "GridSqr";
        Radio1Path = PSWSinfoPath + "Radio1.txt";
        Radio1IDPath = PSWSinfoPath + "Radio1ID.txt";
        AntennaPath = PSWSinfoPath + "Antenna.txt";
        MetadataPath = PSWSinfoPath + "Metadata.txt";
        Beacon1Path = PSWSinfoPath + "Beacon1";

        //read in the user info for the 1st line of this days data collection
        //fprintf -> (ISODate, NodeNum, GridSqr, LatLonElv, CityState, Radio1, Antenna, FrqStd);

        //read in the Node Assigned to this station - if not found indicate so in name returned
        ifstream NodeNumFile (NodeNumPath);
        if (NodeNumFile.is_open())
        {
                getline (NodeNumFile,NodeNum);
                NodeNumFile.close();
        }
        else
                NodeNum = "N00000";  // no node file found - make test Node by default

//        printf("\nNodeNum = %s\n",NodeNum.c_str());  //diag line

        //read in the CallSign - if not found indicate so in CallSign returned
        ifstream CallSignFile (CallSignPath);
        if (CallSignFile.is_open())
        {
                getline (CallSignFile,CallSign);
                CallSignFile.close();
        }
        else
        {
	         CallSign = "NOCall";
	}
//        printf("\nCallSign = %s\n",CallSign.c_str());  //diag line

        //read in the LatLongAlt - if not found indicate so in name returned
        ifstream LatLonElvFile (LatLonElvPath);
        if (LatLonElvFile.is_open())
        {
                getline (LatLonElvFile,LatLonElv);
                LatLonElvFile.close();
        }
        else
        {
	        LatLonElv = "00.00000, -00.00000, 0000";
	}
//	printf("\nLatLonElv = %s\n",LatLonElv.c_str());  //diag line

        //read in the GridSqr - if not found indicate so
        ifstream GridSqrFile (GridSqrPath);
        if (GridSqrFile.is_open())
        {
                getline (GridSqrFile,GridSqr);
                GridSqrFile.close();
        }
        else
                GridSqr = "AA00aa";

//        printf("\nGridSqr = %s\n",GridSqr.c_str());  //diag line

       //read in the City State Names - if not found indicate so in name returned
        ifstream CityStateFile (CityStatePath);
        if (CityStateFile.is_open())
        {
                getline (CityStateFile,CityState);
                CityStateFile.close();
        }
        else
        {
                 CityState = "NOCity NOState";
        }
//        printf("\nCityState = %s\n",CityState.c_str());  //diag line

        //read in the Radio1 Make and Model being used - if not found indicate so in name returned
        ifstream Radio1File (Radio1Path);
        if (Radio1File.is_open())
        {
                getline (Radio1File,Radio1);
                Radio1File.close();
        }
        else
                Radio1 = "Mystery Radio1";

//        printf("\nRadio1 = %s\n",Radio1.c_str());  //diag line

        //read in the Radio1 Make and Model being used - if not found indicate so in name returned
         ifstream Radio1IDFile (Radio1IDPath);
         if (Radio1IDFile.is_open())
         {
                 getline (Radio1IDFile,Radio1ID);
                 Radio1IDFile.close();
         }
         else
                 Radio1ID = "No_Radio1_ID";

//         printf("\nRadio1ID = %s\n",Radio1ID.c_str());  //diag line


        //read in the Antenna Make and Model being used - if not found indicate so in name returned
        ifstream AntennaFile (AntennaPath);
        if (AntennaFile.is_open())
        {
                getline (AntennaFile,Antenna);
                AntennaFile.close();
        }
        else
                Antenna = "50 Ohm Dummy Load";

//        printf("\nAntenna = %s\n",Antenna.c_str());  //diag line

        //read in the frequency standard being used - if not found indicate so in name returned
        ifstream FreqStdFile (FreqStdPath);
        if (FreqStdFile.is_open())
        {
                getline (FreqStdFile,FreqStd);
                FreqStdFile.close();
        }
        else
	        FreqStd = "Unknown FreqStd";

//        printf("\nFreqStd = %s\n",FreqStd.c_str());  //diag line

        //read in the Beacon previously being used - if not found indicate so in name returned
        ifstream Beacon1File (Beacon1Path);
        if (Beacon1File.is_open())
        {
                getline (Beacon1File,SavedBeacon1);
                Beacon1File.close();
        }
        else
                SavedBeacon1 = "Unknown Beacon";

//        printf("\nFreqStd = %s\n",FreqStd.c_str());  //diag line


        // see if frequency is available here - diag print
        CalcFreq = (wf->rfcarrier() + (wf->USB() ? 1.0 : -1.0) * (frequency + fout));
//        printf("\nCalc Frequency at file creation is = %13.3f\n",CalcFreq);

	// Create integer rep for analysis (add offset to get correct rounding)
	CalcFrqNum = int((CalcFreq+100)/10000);
//        printf("\nCalc Freq Num /10000 string at file creation is = %u\n",CalcFrqNum);

	// Calculate the Beacon1 indicator to establish file storge data type (as frequency data)

	switch (CalcFrqNum)
	{
     		case 250:
			{
	     		Beacon1 = "WWV2p5";
			break;
			};

     		case 500:
			{
     			Beacon1 = "WWV5";
			break;
			};

                case 1000:
			{
                	Beacon1 = "WWV10";
			break;
			};

                case 1500:
			{
                	Beacon1 = "WWV15";
			break;
			};

                case 2000:
			{
	               	Beacon1 = "WWV20";
			break;
			};

                case 2500:
			{
                	Beacon1 = "WWV25";
			break;
			};

                case 333:
			{
                	Beacon1 = "CHU3";
			break;
			};

                case 785:
			{
                	Beacon1 = "CHU7";
			break;
			};

                case 1467:
			{
                	Beacon1 = "CHU14";
			break;
			};

      		default:
 	    		Beacon1 = "Unknown";
	}

	printf("\nDecoded Beacon1 for Frequency %8.0f MHz is %s \n",CalcFreq, Beacon1.c_str());


	// diag to force freq of Beacon1
	//        Beacon1 = "WWV2p5";
	//        Beacon1 = "WWV5";
	//        Beacon1 = "WWV10";
	//        Beacon1 = "WWV15";
	//        Beacon1 = "WWV20";
	//        Beacon1 = "WWV25";
	//        Beacon1 = "CHU3";
	//        Beacon1 = "CHU7";
	//        Beacon1 = "CHU14";

	// Create and write the Beacon1 file with new days beacon1 descriptor


	// see if beacon1 file exists
//

	// check if beacon1 freq has changed - save if it did
	if (SavedBeacon1 != Beacon1)
	{
	FILE *out = fl_fopen(Beacon1Path.c_str(), "w"); //create [write] for new data file
		if (unlikely(!out)) {
			LOG_PERROR("fl_fopen");
			return;
		}

	// file opened - write out Beacon1 Name
	fprintf(out, "%s",Beacon1.c_str());
	fclose(out);

        printf("\nWriting New Beacon1 File with Beacon1 = %s\n",Beacon1.c_str());  //diag line

	}
	else

	printf("\nBeacon1 %s has not changed", Beacon1.c_str());


	// read in the Metadata File

	// Establish file storge data type as frequency data
        DataTyp = "FRQ"; // or MAG or TMP

	// open the output file
	createfilename();

	//Open the data file for creation (write) operation
	//first check to see if already created

	if (fl_access(analysisFilename.c_str(), F_OK) == 0)
	{
	// file exists! - use it and keep adding to it
	// indicate in status line that file write to existing file
	        put_status("Using Existing Analysis File");
		write_to_csv = true;  //say to do writes to file
	}
	else
	{
	        put_status("Creating New Analysis File");
		FILE *out = fl_fopen(analysisFilename.c_str(), "w"); //create new data file
		if (unlikely(!out)){
			LOG_PERROR("fl_fopen");
			return;
			}

        // file opened - write out header info
        put_status("Creating analysis file");
//	printf("New File Date is = %s\n",FileDate);  // diag printout

        // Write out the initial header info line to the new .csv file

        // use for initial header containing full ISO date & time  YYYY-MM-DDTHH:MM:SSZ
//        fprintf(out, "#,%s,%s,%s,%s,%s,%s,%s\n",FileDate,NodeNum.c_str(),GridSqr.c_str(),LatLonElv.c_str(),CityState.c_str(),Radio1ID.c_str(),Beacon1.c_str());
        fprintf(out, "#,%sZ,%s,%s,%s,%s,%s,%s\n",FileData,NodeNum.c_str(),GridSqr.c_str(),LatLonElv.c_str(),CityState.c_str(),Radio1ID.c_str(),Beacon1.c_str());

	// Print out saved Metadat contained in ~/PSWS/Sinfo/ directory (alreadd read in)
        // CityState; CallSign; LatLonElv; FreqStd; NodeNum; GridSqr; Radio1; Radio1ID; Antenna; Station;

        fprintf(out, "#######################################\n");
        fprintf(out, "# MetaData for Grape Gen 1 Station\n");
        fprintf(out, "#\n");
        fprintf(out, "# Station Node Number      %s\n", NodeNum.c_str());
        fprintf(out, "# Callsign                 %s\n", CallSign.c_str());
        fprintf(out, "# Grid Square              %s\n", GridSqr.c_str());
        fprintf(out, "# Lat, Long, Elv           %s\n", LatLonElv.c_str());
        fprintf(out, "# City State               %s\n", CityState.c_str());
        fprintf(out, "# Radio1                   %s\n", Radio1.c_str());
        fprintf(out, "# Radio1ID                 %s\n", Radio1ID.c_str());
        fprintf(out, "# Antenna                  %s\n", Antenna.c_str());
        fprintf(out, "# Frequency Standard       %s\n", FreqStd.c_str());
        fprintf(out, "#\n");
        fprintf(out, "# Beacon Now Decoded       %s\n", Beacon1.c_str());
        fprintf(out, "#\n");
        fprintf(out, "#######################################\n");

        // read in the Metadata File

        ifstream MetadataFile (MetadataPath);
	        if (MetadataFile.is_open())
       	 	{
                        fprintf(out, "# --- Extra Metadata File ---\n");
                	while (getline(MetadataFile,Metadata))
				{
					fprintf(out,"# %s\n", Metadata.c_str());
//			        	printf("Metadata = %s\n",Metadata.c_str());  //diag line
				}
			fprintf(out,"#\n"); // Make the file end look nice
                	MetadataFile.close();
        	}
        	else
                Metadata = "No Metadata file";

//        printf("\n1st Metadata line = %s\n",Metadata.c_str());  //diag line

        // Create the headers for the columns in the .CSV file usage
        fprintf(out, "UTC,Freq,Freq Err,Vpk,dBV(Vpk)\n");

        fclose(out);

        printf("Creating analysis file %s \n\n", analysisFilename.c_str());  //diag output

        write_to_csv = true;  //say to do writes to file
        }

//	printf("\nExiting start_csv routine\n\n"); //diag pring
}

void anal::stop_csv()
{
	write_to_csv = false;
	put_status("");
}

void anal::writeFile()
{
	if (!write_to_csv) return;

	time_t now = time(NULL);
	struct tm tm;

// put check for date rollover here
	gmtime_r(&now, &tm);
	char DateNow [12];

//   Create embedded date stamp in the YYYY-MM-DD ISO format
	strftime((char*)DateNow,sizeof(DateNow),"%Y-%m-%d", &tm);

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

// N8OBJ 5-7-19 changed 8.3f to 8.6f (more decimal places on signal strength - show uV level)
// Changed /added new .csv fields 
//	header is: fprintf(out, "UTC,Freq,Freq Err,Vpk,dBV(Vpk)\n");

	fprintf(out, "%02d:%02d:%02d, %13.3f, %6.3f, %8.6f, %6.2f\n",
		tm.tm_hour, tm.tm_min, tm.tm_sec,
		(wf->rfcarrier() + (wf->USB() ? 1.0 : -1.0) * (frequency + fout)), fout, 
		amp, 20.0 * log10( (amp == 0 ? 1e-6 : amp) ) );

        fclose(out);

       // Indicate current time on status line
        char TimeNow[9];
        snprintf( TimeNow, sizeof(TimeNow), "%02d:%02d:%02d", tm.tm_hour, tm.tm_min, tm.tm_sec );
        put_Status1( TimeNow, 5, STATUS_CLEAR);

	// Indicate current file being written on status line
        char StatusMsg [80];
        sprintf( StatusMsg, "Writing File: %s", OpenAnalalysisFile.c_str());
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
