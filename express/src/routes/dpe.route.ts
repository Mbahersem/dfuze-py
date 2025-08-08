
import * as method from '/var/www/app/src/controllers/dpe.controller'
import { Router } from 'express'

const router = Router()

router.get('/get', method.getPointsInZone)
router.get('/parcelles',method.getParcelles)
router.get('/dpe_with_par', method.getDpeWithParcelles)

export default router