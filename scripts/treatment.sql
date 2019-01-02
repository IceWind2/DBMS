CREATE TABLE public.treatment
(
    treatment_id SERIAL,
    medicine character varying(20) NOT NULL,
    start_date character varying(15) NOT NULL,
    side_effect character varying(50),
    side_medicine character varying(50),
    dose character varying(20) NOT NULL,
    previous_id integer,
    change_reason character varying(100),
    CONSTRAINT treatment_pkey PRIMARY KEY (treatment_id),
    CONSTRAINT treatment_fkey FOREIGN KEY (previous_id)
        REFERENCES treatment (treatment_id)
        ON DELETE SET NULL
        ON UPDATE NO ACTION
);
