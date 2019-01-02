CREATE TABLE public.rating
(
    patient_id integer,
    rating_date character varying(15) NOT NULL,
    active_junctions integer NOT NULL,
    damaged_junctions integer NOT NULL,
    doctor_score integer NOT NULL,
    patient_score integer NOT NULL,
    chaq real NOT NULL,
    soe integer NOT NULL,
    srb real NOT NULL,
    treatment_id integer,
    CONSTRAINT rating_fkey FOREIGN KEY (patient_id)
        REFERENCES public.patient (patient_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE SET NULL,
    CONSTRAINT rating_treatment_fkey FOREIGN KEY (treatment_id)
        REFERENCES public.treatment (treatment_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE SET NULL,
    CONSTRAINT patient_date UNIQUE (patient_id, rating_date)
);
