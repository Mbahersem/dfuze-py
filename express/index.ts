/**
 * This file represents the entry point of the backend application.
 * It initializes the connection to the data source, sets up the Express server,
 * and listens for incoming requests on the specified port.
 */

// import 'dotenv/config';
import express,{ Request, Response, NextFunction } from "express";
import bodyParser from "body-parser"; 
import cors from "cors"

import { Constants } from "/var/www/app/src/constants";
import dpeRoute  from '/var/www/app/src/routes/dpe.route';
import { pool } from '/var/www/app/src/data-source';
// Initialize Express app
const app = express();
const port = /*process.env.PORT*/ 3000;

/**
 * Initializes the connection to the data source.
 * If the connection is successful, it logs a success message.
 * If the connection fails, it logs an error message.
 */
const initializeConnection = async () => {
    try {
      // Connectez-vous à la base de données
      const client = await pool.connect();

      // Si la connexion est réussie, affichez un message de succès
      console.log('Connexion à la base de données réussie !');
      
      // Libérez le client/la connexion pour le remettre dans le pool
      client.release();

    } catch (error) {
        console.log('connection has not been established',error);
    }
};

// Call the initializeConnection function to establish the connection
initializeConnection();

// Configure CORS with specific options
const corsOptions = {
    origin: '*',
    methods: 'GET,HEAD,PUT,PATCH,POST,DELETE',
    //credentials: true,
    optionsSuccessStatus: 204,
  };
  
app.use(cors());
// Configure Express middleware
app.use(express.json())
app.use(bodyParser.json())
app.use(bodyParser.urlencoded({extended : true}));

// Set up CORS headers
/*app.use((req : Request,res :Response,next : NextFunction)=>{
    res.header('Access-Control-Allow-Origin','*');
    res.header('Access-Control-Allow-Methods','GET,POST,PUT,DELETE');
    res.header('Access-Control-Allow-Headers','Origin, X-Requested-With, Content, Accept,Content-Type,Authorization');
    return next();
})*/

// Testing
app.get('/api/healthchecker', async (_, res: Response) => {
    res.status(200).json({
      status: 'success',
      message:"succes",
    });
  });

app.get('/api/healthcheck/ready', async (_, res: Response) => {
  try {
    // Connectez-vous à la base de données
    const client = await pool.connect();

    // Si la connexion est réussie, affichez un message de succès
    res.status(200).json({
      status: 'success',
      message:"succes",
    });
    
    // Libérez le client/la connexion pour le remettre dans le pool
    client.release();

  } catch (error) {
    res.status(500).json({
      status: 'error',
      message: error,
    });
  }
})

// Set up the dpe route
app.use(Constants.BASE_URL+'/dpe',dpeRoute);

// Start the Express server
app.listen(port, () => {
    console.log(`Serveur en cours d'exécution sur le port ${port}`);
});
