import py4j.GatewayServer;

import java.util.ArrayList;
import java.util.List;

import com.hankcs.hanlp.HanLP;
import com.hankcs.hanlp.seg.common.Term;
import com.hankcs.hanlp.corpus.dependency.CoNll.CoNLLSentence;
import com.hankcs.hanlp.corpus.dependency.CoNll.CoNLLWord;


public class Hanlp {

    public List<String[]> segment(String line) {
        List<Term> terms = HanLP.segment(line);
        List<String[]> ret = new ArrayList<String[]>();
        for (Term term: terms) {
            String[] tmp = new String[2];
            tmp[0] = term.word;
            tmp[1] = term.nature.toString();
            ret.add(tmp);
        }
        return ret;
    }

    public List<String[]> parse_dependency(String line) {
        CoNLLSentence sentence = HanLP.parseDependency(line);
        List<String[]> ret = new ArrayList<String[]>();
        for (CoNLLWord word: sentence) {
            String[] tmp = new String[6];
            tmp[0] = String.valueOf(word.ID);  // ID
            tmp[1] = word.LEMMA;  // 词
            tmp[2] = word.CPOSTAG;  // 粗词性
            tmp[3] = word.POSTAG;  // 细词性
            tmp[4] = String.valueOf(word.HEAD.ID);  // 依赖词的 ID
            tmp[5] = word.DEPREL;  // 依赖关系
            ret.add(tmp);
        }
        return ret;
    }

    public static void main(String[] args) {
      Hanlp app = new Hanlp();
      // app is now the gateway.entry_point
      GatewayServer server = new GatewayServer(app);
      server.start();
    }
}
