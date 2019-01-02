CREATE TABLE public.condition
(
    patient_id integer,
    rengen_state integer,
    func_group integer,
    antigen character(3),
    uveit character(3),
    treatment_id integer,
    CONSTRAINT condition_fkey FOREIGN KEY (patient_id)
        REFERENCES public.patient (patient_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE ,
    CONSTRAINT condition_treatment_fkey FOREIGN KEY (treatment_id)
        REFERENCES public.treatment (treatment_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE ,
    CONSTRAINT patient_unq UNIQUE (patient_id),
    CONSTRAINT treatment_unq UNIQUE (treatment_id)
);
