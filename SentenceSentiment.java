package core;
import java.io.BufferedWriter; 
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.Reader;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.List;

import org.apache.commons.csv.CSVFormat;
import org.apache.commons.csv.CSVParser;
import org.apache.commons.csv.CSVRecord;


public class SentenceSentiment 
{
	/*
	 * "Very negative" = 0 "Negative" = 1 "Neutral" = 2 "Positive" = 3
	 * "Very positive" = 4
	 */
	// we adjust 1 to 5 according to tripadvisor ratings
	
  public static void main(String[] args) throws IOException 
  {
	  
	 
	  
	    URL resource = SentenceSentiment.class.getClassLoader().getResource("Reviews_all_cleaned_anonym_2.csv");
	    Reader in = new FileReader(resource.getFile(), StandardCharsets.ISO_8859_1);

	    // output
       BufferedWriter writer = new BufferedWriter(new FileWriter("c:/temp/Reviews_all_cleaned_anonym_withsentimentanalysis.csv"));
	  
       CSVFormat theCSV = CSVFormat.DEFAULT.builder()
   				.setHeader()
  				.setSkipHeaderRecord(true)
  				.setDelimiter("\t")
  				.setQuote('"')
  			    .get();

  		Iterable<CSVRecord> records = theCSV.parse(in);
  		
  		// add three columns to the header: recordid, title sentiment analysis and text sentiment analysis
  		List<String> headers = ((CSVParser) records).getHeaderNames();
  		int translatedtitlepos= -1;
  		translatedtitlepos= headers.indexOf("Translated Title");
  		int translatedttextpos= -1;
  		translatedttextpos= headers.indexOf("Translated Text");
  		if (translatedtitlepos == -1 ||  translatedttextpos == -1)
  			throw new RuntimeException("expected column not found ");
 
  		String newheader = "";
  		newheader+= String.format("%s\t", "line");
  		for (String string : headers) {
  			newheader+= String.format("%s\t", string);
		}
  		newheader+= String.format("%s\t", "titleSentiment");
  		newheader+= String.format("%s\n", "reviewSentiment");

  		writer.write(newheader);
  		
  		nlpPipeline.init("en");
 
  	    
	    // coleccion de datos
	    for (CSVRecord aRecord : records) {
	    	String line= String.format("%d\t", aRecord.getRecordNumber()  );
	    	int titleSentiment=0;
	    	int reviewSentiment=0;
	    	int pos= 0;
	    	
	    	for ( String aColumn : aRecord) {
	    		if (pos ==  translatedtitlepos )
	    	 	    titleSentiment= nlpPipeline.estimatingSentiment(aColumn);
	    		else
	    			if (pos ==  translatedttextpos )
	    				reviewSentiment=nlpPipeline.estimatingSentiment(aColumn);
	    		line+= String.format("%s\t", aColumn);
	    		pos++;
	    	}
	    	// add the two last generated columns
	    	line+= String.format("%d\t%d\n", titleSentiment, reviewSentiment);
	    	writer.write(line);
	    	
	    }
	    in.close();
	    writer.close();

  }
}