import javax.swing.*;

import com.softcamp.util.CSLinker; // softcamp.jar 에 포함되어있는 클레스


public class Decrypt{
	public void decrypt(String a, String b){
		System.out.println(a);
		System.out.println(b);
		
	    CSLinker cslinker = new CSLinker();
	    boolean retVal = cslinker.DecryptFileV2("/Users/chaehyejin/Downloads/softcamp/03_Sample\test.txt", "/Users/chaehyejin/Downloads/softcamp/03_Sample\test2.txt");
	    System.out.println("[DSCSLINKERforJAVA]DecryptFile retVal ["+retVal+"]");
		
	}

	public static void main(String[] args) {
		Decrypt decrypt = new Decrypt();
		decrypt.decrypt(args[0], args[1]);
	}
}

 