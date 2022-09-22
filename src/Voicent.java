import java.net.URL;
import java.net.URLEncoder;
import java.net.HttpURLConnection;
import java.io.PrintWriter;
import java.io.InputStream;


public class Voicent
{
    /**
     * Constructor with default localhost:8155
     */
    public Voicent()
    {
        host_ = "localhost";
        port_ = 8155;
    }

    /**
     * Constructor with Voicent gateway hostname and port.
     * @param host Voicent gateway host machine
     * @param port Voicent gateway port number
     */
    public Voicent(String host, int port)
    {
        host_ = host;
        port_ = port;
    }

    /**
     * Make a call to the number specified and play the text message
     * using text-to-speech engine.
     *
     * @param phoneno Phone number to call, exactly as it should be dialed
     * @param text Text to play over the phone using text-to-speech
     * @param selfdelete After the call, delete the call request automatically if set to 1
     * @return Call request ID
     */
    public String callText(String phoneno, String text, boolean selfdelete)
    {
        // call request url
        String urlstr = "/ocall/callreqHandler.jsp";

        // setting the http post string
        String poststr = "info=";
        poststr += URLEncoder.encode("Simple Text Call " + phoneno, "UTF-8");

        poststr += "&phoneno=";
        poststr += phoneno;

        poststr += "&firstocc=10";

        poststr += "&selfdelete=";
        poststr += (selfdelete ? "1" : "0");

        poststr += "&txt=";
        poststr += URLEncoder.encode(text, "UTF-8");

        // Send Call Request
        String rcstr = postToGateway(urlstr, poststr);

        return getReqId(rcstr);
    }

    /**
     * Make a call to the number specified and play the audio file. The
     * audio file should be of PCM 8KHz, 16bit, mono.
     *
     * @param phoneno Phone number to call, exactly as it should be dialed
     * @param audiofile Audio file path name
     * @param selfdelete After the call, delete the call request automatically if set to 1
     * @return Call request ID
     */


    /**
     * Get call status of the call with the reqID.
     *
     * @param reqID Call request ID on the gateway
     * @return call status
     */
    public String callStatus(String reqID)
    {
        // call status url
        String urlstr = "/ocall/callstatusHandler.jsp";

        // setting the http post string
        String poststr = "reqid=";
        poststr += URLEncoder.encode(reqID, "UTF-8");

        // Send Call Request
        String rcstr = postToGateway(urlstr, poststr);

        return getCallStatus(rcstr);
    }

    /**
     * Remove all request from the gateway
     *
     * @param reqID Call request ID on the gateway
     * @return call status
     */
    public void callRemove(String reqID)
    {
        // call status url
        String urlstr = "/ocall/callremoveHandler.jsp";

        // setting the http post string
        String poststr = "reqid=";
        poststr += URLEncoder.encode(reqID, "UTF-8");

        // Send Call remove post
        postToGateway(urlstr, poststr);
    }

    /**
     * Invoke BroadcastByPhone and start the call-till-confirm process
     *
     * @param vcastexe Executable file vcast.exe, BroadcastByPhone path name
     * @param vocfile BroadcastByPhone call list file
     * @param wavfile Audio file used for the broadcast
     * @param ccode Confirmation code
     */
    

    private String postToGateway(String urlstr, String poststr)
    {
        try {
            URL url = new URL("http", host_, port_, urlstr);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();

            conn.setDoInput(true);
            conn.setDoOutput(true);
            conn.setRequestMethod("POST");

            PrintWriter out = new PrintWriter(conn.getOutputStream());
            out.print(poststr);
            out.close();

            InputStream in = conn.getInputStream();

            StringBuffer rcstr = new StringBuffer();
            byte[] b = new byte[4096];
            int len;
            while ((len = in.read(b)) != -1)
                rcstr.append(new String(b, 0, len));
            return rcstr.toString();
        }
        catch (Exception e) {
            e.printStackTrace();
            return "";
        }
    }

    private String getReqId(String rcstr)
    {
        int index1 = rcstr.indexOf("[ReqId=");
        if (index1 == -1)
            return "";
        index1 += 7;

        int index2 = rcstr.indexOf("]", index1);
        if (index2 == -1)
            return "";

        return rcstr.substring(index1, index2);
    }

    private String getCallStatus(String rcstr)
    {
        if (rcstr.indexOf("^made^") != -1)
            return "Call Made";

        if (rcstr.indexOf("^failed^") != -1)
            return "Call Failed";

        if (rcstr.indexOf("^retry^") != -1)
            return "Call Will Retry";

        return "";
    }


    /* test usage */
    public static void main(String args[])
            throws InterruptedException
    {
        String mynumber = "2245481317"; // replace with your own

        Voicent voicent = new Voicent();
        String reqId = voicent.callText(mynumber, "hello, how are you", true);
        System.out.println("callText: " + reqId);
    }


    private String host_;
    private int port_;
}
 