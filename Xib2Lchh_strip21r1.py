"""
Stripping filtering Template for B2OC filtering requests
@author Bhagyashree Pagare
@date   2020-04-20
"""
#stripping version
stripping='stripping21r1'

#use CommonParticlesArchive
from CommonParticlesArchive import CommonParticlesArchiveConf
CommonParticlesArchiveConf().redirect(stripping)
 
from Gaudi.Configuration import *
MessageSvc().Format = "% F%30W%S%7W%R%T %0W%M"

#####################################
# Tighten Trk Chi2 to <3
from CommonParticles.Utils import DefaultTrackingCuts
DefaultTrackingCuts().Cuts  = { "Chi2Cut" : [ 0, 3 ],
                                "CloneDistCut" : [5000, 9e+99 ] }
# present only in 21 and 21r1.   Is it needed? if yes, on what basis are chosen?
 #####################################

#Raw event juggler to split Other/RawEvent into Velo/RawEvent and Tracker/RawEvent
#
from Configurables import RawEventJuggler
juggler = RawEventJuggler( DataOnDemand=True, Input=2.0, Output=4.0 )
#
# Build the streams and stripping object
#
from StrippingConf.Configuration import StrippingConf, StrippingStream
from StrippingSettings.Utils import strippingConfiguration
from StrippingArchive.Utils import buildStreams, cloneLinesFromStream
from StrippingArchive import strippingArchive
 
 
#get the configuration dictionary from the database
config  = strippingConfiguration(stripping)
#get the line builders from the archive
archive = strippingArchive(stripping)
 
streams = buildStreams(stripping = config, archive = archive)

#OUTPUT STREAM NAME
AllStreams = StrippingStream("xib2lchh.Strip")			 

linesToAdd = []

#LIST OF FILTERED LINES

MyLines = [ 'StrippingX2LcPiPiSSLc2PKPiBeauty2CharmLine',
	    'StrippingX2LcKPiSSLc2PKPiBeauty2CharmLine',
            'StrippingX2LcKKSSLc2PKPiBeauty2CharmLine',
            'StrippingB2DHHOSD2HHHCFPIDBeauty2CharmLine'
            ]

 
for stream in streams:
    if 'Bhadron' in stream.name():
        for line in stream.lines:
            line._prescale = 1.0
            if line.name() in MyLines:
                linesToAdd.append(line)
AllStreams.appendLines(linesToAdd)
 
 
 
sc = StrippingConf( Streams = [ AllStreams ],
                    MaxCandidates = 2000,
                    TESPrefix = 'Strip'
                    )
 
 
AllStreams.sequence().IgnoreFilterPassed = False # so that we do not get all events written out
 
#
 
# Configuration of SelDSTWriter
#
enablePacking = True
from DSTWriters.microdstelements import *
from DSTWriters.Configuration import (SelDSTWriter,
                                      stripDSTStreamConf,
                                      stripDSTElements,
                                      stripMicroDSTStreamConf,
                                      stripMicroDSTElements,
                                      stripCalibMicroDSTStreamConf 
                                      )

SelDSTWriterElements = {
    'default'               : stripMicroDSTElements(pack=enablePacking,isMC=True)
    }

SelDSTWriterConf = {
    'default'               : stripMicroDSTStreamConf(pack=enablePacking, isMC=True)
    }

#Items that might get lost when running the CALO+PROTO ReProcessing in DV
caloProtoReprocessLocs = [ "/Event/pRec/ProtoP#99", "/Event/pRec/Calo#99" ]
 
# Make sure they are present on full DST streams
SelDSTWriterConf['default'].extraItems += caloProtoReprocessLocs
 
dstWriter = SelDSTWriter( "MyDSTWriter",
                          StreamConf = SelDSTWriterConf,
                          MicroDSTElements = SelDSTWriterElements,
                          OutputFileSuffix ='Filtered',
                          SelectionSequences = sc.activeStreams()
                          )
 
# Add stripping TCK
from Configurables import StrippingTCK

stck = StrippingTCK(HDRLocation = '/Event/Strip/Phys/DecReports', TCK=0x36132110)

#
# DaVinci Configuration
#
from Configurables import DaVinci
DaVinci().Simulation = True
DaVinci().EvtMax = -1                     # Number of events
DaVinci().HistogramFile = "DVHistos.root"
DaVinci().appendToMainSequence( [ sc.sequence() ] )
DaVinci().appendToMainSequence( [ stck ] )
DaVinci().appendToMainSequence( [ dstWriter.sequence() ] )
DaVinci().ProductionType = "Stripping"
 
# Change the column size of Timing table
from Configurables import TimingAuditor, SequencerTimerTool
TimingAuditor().addTool(SequencerTimerTool,name="TIMER")
TimingAuditor().TIMER.NameSize = 60

