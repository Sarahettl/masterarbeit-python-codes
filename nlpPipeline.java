package core;
import java.util.Properties;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;
import edu.stanford.nlp.ling.CoreAnnotations;
import edu.stanford.nlp.pipeline.Annotation;
import edu.stanford.nlp.neural.rnn.RNNCoreAnnotations;
import edu.stanford.nlp.sentiment.SentimentCoreAnnotations;
import edu.stanford.nlp.sentiment.SentimentCoreAnnotations.SentimentAnnotatedTree;
import edu.stanford.nlp.trees.Tree;
import edu.stanford.nlp.util.CoreMap;

public class nlpPipeline {
    static StanfordCoreNLP pipeline;
    public static void init(String language) 
    {
        Properties props = new Properties();
        props.setProperty("annotators", "tokenize, ssplit, parse, sentiment");
        props.setProperty("tokenize.language", language); 
        pipeline = new StanfordCoreNLP(props);
    }
    
    public static int estimatingSentiment(String text)
    {
      int sentimentInt;
      String sentimentName; 
      Annotation annotation = pipeline.process(text);
      int sum= 0;
      int phrasesqty= 0;
      for(CoreMap sentence : annotation.get(CoreAnnotations.SentencesAnnotation.class))
      {
    	  	Tree tree = sentence.get(SentimentAnnotatedTree.class);
         	sentimentInt = RNNCoreAnnotations.getPredictedClass(tree) + 1; 
         	sum+= sentimentInt;
         	phrasesqty++;
        	sentimentName = sentence.get(SentimentCoreAnnotations.SentimentClass.class);
 //       	System.out.println(sentimentName + "\t" + sentimentInt + "\t" + sentence);
      }
//      System.out.println("General sentimen analysis:" + (int) ( 0.5 + ( 1.0 *  sum ) / phrasesqty) + "\t" + text);
      return(int) ( 0.5 + ( 1.0 *  sum ) / phrasesqty) ;
     }
}