/**
 * Represents the application data source.
 */

// import 'dotenv/config';
const Pool = require('pg').Pool


export const pool = new Pool({
    user: /*process.env.DB_USERNAME*/"postgres",
    database: /*process.env.DB_NAME*/"postgres",
    password: /*process.env.DB_PASSWORD*/"j2m2025",
    host: /*process.env.HOST*/"localhost",
    port: parseInt(/*process.env.DB_PORT ||*/ '5432', 10),
  })
