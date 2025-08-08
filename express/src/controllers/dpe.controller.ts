/**
 * Finds all Dpe records within the specified coordinates.
 * @param req - The Express request object.
 * @param res - The Express response object.
 * @returns A JSON response containing the list of Dpe records.
 */
import { Response, Request } from "express";
import { pool } from "/var/www/app/src/data-source";

/**
 * Extracts top and bottom coordinates from the request.
 * @param req - The Express request object.
 * @returns An object containing top and bottom coordinates.
 */
const getTopAndBottom = (req: any): { top: number[], bottom: number[] } => {
    const topLeft: string = req.query.topLeft as string;
    const bottomRight: string = req.query.bottomRight as string;

    // Check if parameters are provided
    if (!topLeft || !bottomRight) {
        throw new Error('Les paramètres topLeft et bottomRight doivent être fournis dans la requête.');
    }

    // Convert coordinates to numbers
    const top: number[] = topLeft.split(',').map(Number);
    const bottom: number[] = bottomRight.split(',').map(Number);

    // Check if coordinates have the correct size
    if (top.length !== 2 || bottom.length !== 2) {
        throw new Error('Les coordonnées doivent être fournies sous forme de paires (x, y).');
    }

    return { top, bottom };
}

/**
 * Retrieves points within the specified zone.
 * @param req - The Express request object.
 * @param res - The Express response object.
 */
export const getPointsInZone = (req: Request, res: Response) => {
    const { top, bottom } = getTopAndBottom(req);

    pool.query('SELECT * FROM dpe_resume WHERE ST_Contains(ST_MakeEnvelope(LEAST($1::numeric, $2::numeric), LEAST($3::numeric, $4::numeric), GREATEST($1::numeric, $2::numeric),GREATEST($3::numeric, $4::numeric), 2154),geom) order by random() limit 500', 
      [top[1], bottom[1], top[0], bottom[0]], 
      (error, results) => {
        if (error) {
          throw error;
        }
        res.status(200).json(results.rows);
      }
    );
};

/**
 * Retrieves parcels within the specified zone and surface range.
 * @param req - The Express request object.
 * @param res - The Express response object.
 */
export const getParcelles = (req: Request, res: Response) => {
    const surface = req.query.surface as string;
    const { top, bottom } = getTopAndBottom(req);
    const surface_range = surface.split(',').map(Number);

    pool.query('SELECT * FROM parcelles WHERE ST_Contains(ST_MakeEnvelope(LEAST($1::numeric, $2::numeric), LEAST($3::numeric, $4::numeric), GREATEST($1::numeric, $2::numeric),GREATEST($3::numeric, $4::numeric), 2154),geom) AND contenance >= $5::numeric AND contenance <= $6::numeric order by random() limit 500', 
      [top[1], bottom[1], top[0], bottom[0], surface_range[0], surface_range[1]], 
      (error, results) => {
        if (error) {
          throw error;
        }
        res.status(200).json(results.rows);
      }
    );
};

/**
 * Retrieves Dpe records with parcels within the specified zone and surface range.
 * @param req - The Express request object.
 * @param res - The Express response object.
 */
export const getDpeWithParcelles = (req: Request, res: Response) => {
    const surface = req.query.surface as string;
    const { top, bottom } = getTopAndBottom(req);
    const surface_range = surface.split(',').map(Number);
    
    pool.query('SELECT * FROM dpe_resume WHERE ST_Contains(ST_MakeEnvelope(LEAST($1::numeric, $2::numeric), LEAST($3::numeric, $4::numeric), GREATEST($1::numeric, $2::numeric),GREATEST($3::numeric, $4::numeric), 2154),geom) AND contenance >= $5::numeric AND contenance <= $6::numeric order by random() limit 500', 
      [top[1], bottom[1], top[0], bottom[0], surface_range[0], surface_range[1]], 
      (error, results) => {
        if (error) {
          throw error;
        }
        res.status(200).json(results.rows);
      }
    );
};
